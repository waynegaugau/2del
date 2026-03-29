from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from .models import (
    User, Clinic, Staff, Service,
    Pet, VaccinationRecord,
    Appointment, MedicalRecord,
    Medication, Prescription, Payment
)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password', 'password2', 'role']
        extra_kwargs = {
            'role': {'default': User.Role.OWNER}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Mật khẩu không khớp.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs['username'],
            password=attrs['password']
        )
        if not user:
            raise serializers.ValidationError('Tên đăng nhập hoặc mật khẩu không đúng.')
        if not user.is_active:
            raise serializers.ValidationError('Tài khoản đã bị vô hiệu hóa.')
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'role']
        read_only_fields = ['id', 'role']


class ClinicSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Clinic
        fields = [
            'id', 'name', 'address', 'phone', 'email',
            'owner', 'owner_username', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.STAFF),
        source='user',
        write_only=True
    )
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)

    class Meta:
        model = Staff
        fields = [
            'id', 'user', 'user_id',
            'clinic', 'clinic_name',
            'role', 'license_number', 'is_active'
        ]
        read_only_fields = ['id']


class StaffSimpleSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'full_name', 'role']


class ServiceSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'clinic', 'clinic_name',
            'name', 'category', 'description',
            'price', 'duration_minutes', 'is_active'
        ]
        read_only_fields = ['id']


class ServiceSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'category', 'price', 'duration_minutes']


class VaccinationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationRecord
        fields = [
            'id', 'pet', 'vaccine_name',
            'administered_date', 'next_due_date', 'notes'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs.get('next_due_date') and attrs['next_due_date'] <= attrs['administered_date']:
            raise serializers.ValidationError({
                'next_due_date': 'Ngày tiêm tiếp theo phải sau ngày tiêm hiện tại.'
            })
        return attrs


class PetSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    vaccinations = VaccinationRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Pet
        fields = [
            'id', 'owner', 'owner_username',
            'name', 'species', 'breed',
            'date_of_birth', 'gender', 'weight',
            'vaccinations'
        ]
        read_only_fields = ['id', 'owner']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class PetSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ['id', 'name', 'species', 'breed']


class AppointmentSerializer(serializers.ModelSerializer):
    pet_detail = PetSimpleSerializer(source='pet', read_only=True)
    staff_detail = StaffSimpleSerializer(source='staff', read_only=True)
    service_detail = ServiceSimpleSerializer(source='service', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'pet', 'pet_detail',
            'clinic',
            'staff', 'staff_detail',
            'service', 'service_detail',
            'appointment_date', 'status',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']

    def validate(self, attrs):
        from django.utils import timezone
        if attrs.get('appointment_date') and attrs['appointment_date'] < timezone.now():
            raise serializers.ValidationError({
                'appointment_date': 'Không thể đặt lịch trong quá khứ.'
            })
        return attrs


class AppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'status']

    def validate_status(self, value):
        allowed = [
            Appointment.Status.CONFIRMED,
            Appointment.Status.CHECKED_IN,
            Appointment.Status.CANCELLED,
            Appointment.Status.COMPLETED,
        ]
        if value not in allowed:
            raise serializers.ValidationError('Trạng thái không hợp lệ.')
        return value


class MedicationSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.SerializerMethodField()

    class Meta:
        model = Medication
        fields = [
            'id', 'name', 'manufacturer', 'unit',
            'stock_quantity', 'min_stock_level',
            'price_per_unit', 'description', 'is_low_stock'
        ]
        read_only_fields = ['id']

    def get_is_low_stock(self, obj):
        return obj.is_running_low()


class PrescriptionSerializer(serializers.ModelSerializer):
    medication_name = serializers.CharField(source='medication.name', read_only=True)
    medication_unit = serializers.CharField(source='medication.unit', read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'medical_record',
            'medication', 'medication_name', 'medication_unit',
            'quantity_prescribed', 'dosage',
            'instructions', 'duration'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        medication = attrs.get('medication')
        quantity = attrs.get('quantity_prescribed', 0)
        if medication and quantity > medication.stock_quantity:
            raise serializers.ValidationError({
                'quantity_prescribed': (
                    f'Số lượng kê ({quantity}) vượt quá tồn kho '
                    f'({medication.stock_quantity} {medication.unit}).'
                )
            })
        return attrs


class PrescriptionInlineSerializer(serializers.ModelSerializer):
    medication_name = serializers.CharField(source='medication.name', read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'medication', 'medication_name',
            'quantity_prescribed', 'dosage',
            'instructions', 'duration'
        ]
        read_only_fields = ['id']


class MedicalRecordSerializer(serializers.ModelSerializer):
    pet_detail = PetSimpleSerializer(source='pet', read_only=True)
    staff_detail = StaffSimpleSerializer(source='staff', read_only=True)
    prescriptions = PrescriptionInlineSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'pet', 'pet_detail',
            'clinic', 'staff', 'staff_detail',
            'appointment',
            'diagnosis', 'treatment_plan', 'notes',
            'prescriptions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'staff_profile'):
            validated_data['staff'] = request.user.staff_profile
        return super().create(validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    appointment_detail = AppointmentSerializer(source='appointment', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'appointment', 'appointment_detail',
            'amount', 'payment_method',
            'status', 'created_at', 'paid_at'
        ]
        read_only_fields = ['id', 'created_at', 'paid_at', 'status']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Số tiền thanh toán phải lớn hơn 0.')
        return value


class PaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_method', 'status']

    def validate(self, attrs):
        if attrs.get('status') == Payment.Status.PAID and not attrs.get('payment_method'):
            raise serializers.ValidationError({
                'payment_method': 'Cần chọn phương thức thanh toán khi xác nhận đã thanh toán.'
            })
        return attrs

    def update(self, instance, validated_data):
        from django.utils import timezone
        if validated_data.get('status') == Payment.Status.PAID:
            validated_data['paid_at'] = timezone.now()
        return super().update(instance, validated_data)