from rest_framework.views import APIView

from src.common.permissions import IsClinicStaffRole
from src.common.responses import success_response
from src.serializers.medical_record_serializer import (
    MedicalRecordCreateSerializer,
    MedicalRecordSerializer,
    MedicalRecordUpdateSerializer,
)
from src.services.medical_record_service import MedicalRecordService


class AppointmentMedicalRecordAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def get(self, request, appointment_id):
        record = MedicalRecordService.get_medical_record_by_appointment(request.user, appointment_id)
        serializer = MedicalRecordSerializer(record)
        return success_response(serializer.data, "Lay ho so benh an thanh cong")

    def post(self, request, appointment_id):
        serializer = MedicalRecordCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record = MedicalRecordService.create_medical_record(
            request.user,
            appointment_id,
            serializer.validated_data,
        )
        output = MedicalRecordSerializer(record)
        return success_response(output.data, "Tao ho so benh an thanh cong", 201)


class MedicalRecordDetailAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def get(self, request, record_id):
        record = MedicalRecordService.get_medical_record_detail(request.user, record_id)
        serializer = MedicalRecordSerializer(record)
        return success_response(serializer.data, "Lay chi tiet ho so benh an thanh cong")

    def put(self, request, record_id):
        serializer = MedicalRecordUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record = MedicalRecordService.update_medical_record(
            request.user,
            record_id,
            serializer.validated_data,
        )
        output = MedicalRecordSerializer(record)
        return success_response(output.data, "Cap nhat ho so benh an thanh cong")


class PetMedicalRecordListAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def get(self, request, pet_id):
        records = MedicalRecordService.get_pet_medical_records(request.user, pet_id)
        serializer = MedicalRecordSerializer(records, many=True)
        return success_response(serializer.data, "Lay lich su ho so benh an cua thu cung thanh cong")
