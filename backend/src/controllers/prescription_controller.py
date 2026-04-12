from rest_framework import status
from rest_framework.views import APIView

from src.common.permissions import IsClinicStaffRole
from src.common.responses import success_response
from src.serializers.prescription_item_serializer import (
    PrescriptionItemCreateSerializer,
    PrescriptionItemSerializer,
    PrescriptionItemUpdateSerializer,
)
from src.serializers.prescription_serializer import (
    PrescriptionCreateSerializer,
    PrescriptionSerializer,
    PrescriptionUpdateSerializer,
)
from src.services.prescription_service import PrescriptionService


class MedicalRecordPrescriptionAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def get(self, request, medical_record_id):
        prescription = PrescriptionService.get_prescription_by_medical_record(
            request.user,
            medical_record_id,
        )
        serializer = PrescriptionSerializer(prescription)
        return success_response(serializer.data, "Lay don thuoc thanh cong")

    def post(self, request, medical_record_id):
        serializer = PrescriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        prescription = PrescriptionService.create_prescription(
            request.user,
            medical_record_id,
            serializer.validated_data,
        )
        output = PrescriptionSerializer(prescription)
        return success_response(
            output.data,
            "Tao don thuoc thanh cong",
            status.HTTP_201_CREATED,
        )


class PrescriptionDetailAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def get(self, request, prescription_id):
        prescription = PrescriptionService.get_prescription_detail(request.user, prescription_id)
        serializer = PrescriptionSerializer(prescription)
        return success_response(serializer.data, "Lay chi tiet don thuoc thanh cong")

    def put(self, request, prescription_id):
        serializer = PrescriptionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        prescription = PrescriptionService.update_prescription(
            request.user,
            prescription_id,
            serializer.validated_data,
        )
        output = PrescriptionSerializer(prescription)
        return success_response(output.data, "Cap nhat don thuoc thanh cong")


class PrescriptionItemListCreateAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def post(self, request, prescription_id):
        serializer = PrescriptionItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = PrescriptionService.add_prescription_item(
            request.user,
            prescription_id,
            serializer.validated_data,
        )
        output = PrescriptionItemSerializer(item)
        return success_response(
            output.data,
            "Them thuoc vao don thanh cong",
            status.HTTP_201_CREATED,
        )


class PrescriptionItemDetailAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def put(self, request, item_id):
        serializer = PrescriptionItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = PrescriptionService.update_prescription_item(
            request.user,
            item_id,
            serializer.validated_data,
        )
        output = PrescriptionItemSerializer(item)
        return success_response(output.data, "Cap nhat chi tiet don thuoc thanh cong")

    def delete(self, request, item_id):
        PrescriptionService.delete_prescription_item(request.user, item_id)
        return success_response(message="Xoa chi tiet don thuoc thanh cong")
