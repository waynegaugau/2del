from rest_framework.views import APIView
from rest_framework import status

from src.common.permissions import IsAdminUserRole, IsReadOnlyOrAdminRole
from src.serializers.clinic_serializer import (
    ClinicSerializer,
    ClinicCreateSerializer,
    ClinicUpdateSerializer,
    ServiceSerializer,
    ServiceCreateSerializer,
    ServiceUpdateSerializer,
)
from src.services.clinic_service import ClinicService, ServiceService
from src.common.responses import success_response


class ClinicListCreateAPIView(APIView):
    """
    GET  : Ai cng c th xem danh sach phong kham
    POST : Chi ADMIN moi duoc tao phong kham
    """

    permission_classes = [IsReadOnlyOrAdminRole]

    def get(self, request):
        clinics = ClinicService.get_all_clinics()
        serializer = ClinicSerializer(clinics, many=True)
        return success_response(serializer.data, "Lay danh sach phong kham thanh cong")

    def post(self, request):
        serializer = ClinicCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        clinic = ClinicService.create_clinic(serializer.validated_data)
        output = ClinicSerializer(clinic)
        return success_response(
            output.data,
            "Tao phong kham thanh cong",
            status.HTTP_201_CREATED,
        )


class ClinicDetailAPIView(APIView):
    """
    GET    : Ai cng c th xem chi tiet phong kham
    PUT    : Chi ADMIN moi duoc cap nhat phong kham
    DELETE : Chi ADMIN moi duoc xoa phong kham
    """

    permission_classes = [IsReadOnlyOrAdminRole]

    def get(self, request, clinic_id):
        clinic = ClinicService.get_clinic_detail(clinic_id)
        serializer = ClinicSerializer(clinic)
        return success_response(serializer.data, "Lay chi tiet phong kham thanh cong")

    def put(self, request, clinic_id):
        serializer = ClinicUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        clinic = ClinicService.update_clinic(clinic_id, serializer.validated_data)
        output = ClinicSerializer(clinic)
        return success_response(output.data, "Cap nhat phong kham thanh cong")

    def delete(self, request, clinic_id):
        ClinicService.delete_clinic(clinic_id)
        return success_response(message="Xoa phong kham thanh cong")


class ServiceCreateAPIView(APIView):
    """
    POST : Chi ADMIN moi duoc tao dich vu
    """

    permission_classes = [IsAdminUserRole]

    def post(self, request):
        serializer = ServiceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ServiceService.create_service(serializer.validated_data)
        output = ServiceSerializer(service)
        return success_response(
            output.data,
            "Tao dich vu thanh cong",
            status.HTTP_201_CREATED,
        )


class ServiceUpdateDeleteAPIView(APIView):
    """
    PUT    : Chi ADMIN moi duoc cap nhat dich vu
    DELETE : Chi ADMIN moi duoc xoa dich vu
    """

    permission_classes = [IsAdminUserRole]

    def put(self, request, service_id):
        serializer = ServiceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ServiceService.update_service(service_id, serializer.validated_data)
        output = ServiceSerializer(service)
        return success_response(output.data, "Cap nhat dich vu thanh cong")

    def delete(self, request, service_id):
        ServiceService.delete_service(service_id)
        return success_response(message="Xoa dich vu thanh cong")


class ServiceByClinicAPIView(APIView):
    """
    GET : Ai cng c th xem danh sach dich vu cua mot phong kham
    """

    def get(self, request, clinic_id):
        services = ServiceService.get_services_by_clinic(clinic_id)
        serializer = ServiceSerializer(services, many=True)
        return success_response(serializer.data, "Lay danh sach dich vu thanh cong")
