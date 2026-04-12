from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from src.common.permissions import IsClinicStaffRole, IsPetOwnerRole
from src.serializers.appointment_serializer import (
    AppointmentSerializer,
    AppointmentCreateSerializer,
    AppointmentUpdateSerializer,
)
from src.services.appointment_service import AppointmentService
from src.common.responses import success_response


class AppointmentListCreateAPIView(APIView):
    permission_classes = [IsPetOwnerRole]

    def get(self, request):
        appointments = AppointmentService.get_user_appointments(request.user)
        serializer = AppointmentSerializer(appointments, many=True)
        return success_response(serializer.data, "Lay danh sach lich hen thanh cong")

    def post(self, request):
        serializer = AppointmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment = AppointmentService.create_appointment(
            request.user,
            serializer.validated_data
        )
        output = AppointmentSerializer(appointment)
        return success_response(
            output.data,
            "Tao lich hen thanh cong",
            status.HTTP_201_CREATED,
        )


class StaffClinicAppointmentListAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def get(self, request):
        appointments = AppointmentService.get_clinic_appointments(request.user)
        serializer = AppointmentSerializer(appointments, many=True)
        return success_response(serializer.data, "Lay danh sach lich hen theo phong kham thanh cong")


class StaffClinicAppointmentDetailAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def get(self, request, appointment_id):
        appointment = AppointmentService.get_clinic_appointment_detail(request.user, appointment_id)
        serializer = AppointmentSerializer(appointment)
        return success_response(serializer.data, "Lay chi tiet lich hen theo phong kham thanh cong")


class AppointmentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, appointment_id):
        appointment = AppointmentService.get_appointment_detail(
            request.user,
            appointment_id
        )
        serializer = AppointmentSerializer(appointment)
        return success_response(serializer.data, "Lay chi tiet lich hen thanh cong")

    def put(self, request, appointment_id):
        serializer = AppointmentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment = AppointmentService.update_appointment(
            request.user,
            appointment_id,
            serializer.validated_data
        )
        output = AppointmentSerializer(appointment)
        return success_response(output.data, "Cap nhat lich hen thanh cong")

    def delete(self, request, appointment_id):
        appointment = AppointmentService.cancel_appointment(
            request.user,
            appointment_id
        )
        output = AppointmentSerializer(appointment)
        return success_response(output.data, "Huy lich hen thanh cong")


class AppointmentCheckInAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def post(self, request, appointment_id):
        appointment = AppointmentService.check_in(request.user, appointment_id)
        serializer = AppointmentSerializer(appointment)
        return success_response(serializer.data, "Check-in thanh cong")


class AppointmentConfirmAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def post(self, request, appointment_id):
        appointment = AppointmentService.confirm_appointment(request.user, appointment_id)
        serializer = AppointmentSerializer(appointment)
        return success_response(serializer.data, "Xac nhan lich hen thanh cong")


class AppointmentStartAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def post(self, request, appointment_id):
        appointment = AppointmentService.start_appointment(request.user, appointment_id)
        serializer = AppointmentSerializer(appointment)
        return success_response(serializer.data, "Bat dau kham thanh cong")


class AppointmentCompleteAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def post(self, request, appointment_id):
        appointment = AppointmentService.complete_appointment(request.user, appointment_id)
        serializer = AppointmentSerializer(appointment)
        return success_response(serializer.data, "Hoan tat lich hen thanh cong")


class AppointmentNoShowAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def post(self, request, appointment_id):
        appointment = AppointmentService.mark_no_show(request.user, appointment_id)
        serializer = AppointmentSerializer(appointment)
        return success_response(serializer.data, "Danh dau vang mat thanh cong")
