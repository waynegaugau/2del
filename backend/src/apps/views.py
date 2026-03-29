from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from rest_framework.exceptions import PermissionDenied

from .models import (
    User, Clinic, Staff, Service,
    Pet, VaccinationRecord,
    Appointment, MedicalRecord,
    Medication, Prescription, Payment
)
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ClinicSerializer,
    StaffSerializer,
    ServiceSerializer,
    PetSerializer, VaccinationRecordSerializer,
    AppointmentSerializer, AppointmentStatusSerializer,
    MedicalRecordSerializer,
    MedicationSerializer, PrescriptionSerializer,
    PaymentSerializer, PaymentUpdateSerializer,
)


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.ADMIN


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.STAFF


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.OWNER


class IsAdminOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.ADMIN, User.Role.STAFF
        ]


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                'user': UserSerializer(user).data,
                'token': token.key,
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
        })


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Xóa token hiện tại
            request.user.auth_token.delete()
            return Response({'detail': 'Đã đăng xuất thành công.'}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'detail': 'Không tìm thấy token.'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        print(f"DEBUG: User: {user.username} (ID: {user.id})")
        
        if user.is_anonymous:
            return Response(
                {"detail": "Token không hợp lệ"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClinicViewSet(viewsets.ModelViewSet):
    serializer_class = ClinicSerializer
    queryset = Clinic.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]


class StaffViewSet(viewsets.ModelViewSet):
    serializer_class = StaffSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Staff.objects.select_related('user', 'clinic').all()

    @action(detail=True, methods=['patch'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        staff = self.get_object()
        staff.is_active = not staff.is_active
        staff.save()
        return Response({
            'id': staff.id,
            'is_active': staff.is_active,
            'detail': f"Tài khoản đã {'kích hoạt' if staff.is_active else 'vô hiệu hóa'}."
        })


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer

    def get_queryset(self):
        qs = Service.objects.select_related('clinic').all()
        category = self.request.query_params.get('category')
        clinic_id = self.request.query_params.get('clinic')
        if category:
            qs = qs.filter(category=category)
        if clinic_id:
            qs = qs.filter(clinic_id=clinic_id)
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]


class PetViewSet(viewsets.ModelViewSet):
    serializer_class = PetSerializer

    def get_permissions(self):
        if self.action in ['vaccinations', 'appointments', 'medical_records']:
            return [permissions.IsAuthenticated()]
        return [IsOwner()]

    def get_queryset(self):
        return Pet.objects.filter(owner=self.request.user)

    @action(detail=True, methods=['get'], url_path='vaccinations')
    def vaccinations(self, request, pk=None):
        pet = self.get_object()
        records = pet.vaccinations.all().order_by('-administered_date')
        serializer = VaccinationRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='appointments')
    def appointments(self, request, pk=None):
        pet = self.get_object()
        appts = pet.appointments.all().order_by('-appointment_date')
        serializer = AppointmentSerializer(appts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='medical-records')
    def medical_records(self, request, pk=None):
        pet = self.get_object()
        records = pet.medical_records.all().order_by('-created_at')
        serializer = MedicalRecordSerializer(records, many=True)
        return Response(serializer.data)


class VaccinationRecordViewSet(viewsets.ModelViewSet):
    serializer_class = VaccinationRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.OWNER:
            return VaccinationRecord.objects.filter(pet__owner=user)
        return VaccinationRecord.objects.select_related('pet').all()


class AppointmentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update', 'check_in']:
            return AppointmentStatusSerializer
        return AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Appointment.objects.select_related(
            'pet', 'clinic', 'staff', 'service'
        )
        if user.role == User.Role.OWNER:
            return qs.filter(pet__owner=user)
        if user.role == User.Role.STAFF:
            try:
                return qs.filter(clinic=user.staff_profile.clinic)
            except Staff.DoesNotExist:
                return qs.none()
        return qs.all()

    def get_permissions(self):
        if self.action == 'create':
            return [IsOwner()]
        if self.action in ['update', 'partial_update', 'check_in']:
            return [IsAdminOrStaff()]
        if self.action == 'destroy':
            return [IsOwner()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'], url_path='check-in')
    def check_in(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status != Appointment.Status.CONFIRMED:
            return Response(
                {'detail': 'Chỉ có thể check-in lịch hẹn đã được xác nhận.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        appointment.check_in()
        return Response(
            AppointmentSerializer(appointment).data,
            status=status.HTTP_200_OK
        )


class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrStaff()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = MedicalRecord.objects.select_related(
            'pet', 'clinic', 'staff', 'appointment'
        ).prefetch_related('prescriptions')

        if user.role == User.Role.OWNER:
            return qs.filter(pet__owner=user)
        if user.role == User.Role.STAFF:
            try:
                return qs.filter(clinic=user.staff_profile.clinic)
            except Staff.DoesNotExist:
                return qs.none()
        return qs.all()


class MedicationViewSet(viewsets.ModelViewSet):
    serializer_class = MedicationSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdmin()]
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAdminOrStaff()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = Medication.objects.all()
        name = self.request.query_params.get('name')
        if name:
            qs = qs.filter(name__icontains=name)
        return qs

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        medications = [m for m in self.get_queryset() if m.is_running_low()]
        serializer = self.get_serializer(medications, many=True)
        return Response(serializer.data)


class PrescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = PrescriptionSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrStaff()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Prescription.objects.select_related(
            'medication', 'medical_record__pet'
        )
        if user.role == User.Role.OWNER:
            return qs.filter(medical_record__pet__owner=user)
        if user.role == User.Role.STAFF:
            try:
                return qs.filter(medical_record__clinic=user.staff_profile.clinic)
            except Staff.DoesNotExist:
                return qs.none()
        return qs.all()

    def perform_create(self, serializer):
        prescription = serializer.save()
        medication = prescription.medication
        medication.stock_quantity -= prescription.quantity_prescribed
        medication.save()


class PaymentViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return PaymentUpdateSerializer
        return PaymentSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminOrStaff()]
        if self.action in ['update', 'partial_update']:
            return [IsAdminOrStaff()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.select_related('appointment__pet')
        if user.role == User.Role.OWNER:
            return qs.filter(appointment__pet__owner=user)
        if user.role == User.Role.STAFF:
            try:
                return qs.filter(appointment__clinic=user.staff_profile.clinic)
            except Staff.DoesNotExist:
                return qs.none()
        return qs.all()