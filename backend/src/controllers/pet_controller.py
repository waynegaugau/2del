from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from src.serializers.pet_serializer import (
    PetSerializer,
    PetCreateSerializer,
    PetUpdateSerializer,
)
from src.services.pet_service import PetService
from src.common.responses import success_response


class PetListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pets = PetService.get_user_pets(request.user)
        serializer = PetSerializer(pets, many=True)
        return success_response(serializer.data, "Lay danh sach thu cung thanh cong")

    def post(self, request):
        serializer = PetCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pet = PetService.create_pet(request.user, serializer.validated_data)
        output = PetSerializer(pet)
        return success_response(
            output.data,
            "Tao thu cung thanh cong",
            status.HTTP_201_CREATED,
        )


class PetDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pet_id):
        pet = PetService.get_pet_detail(request.user, pet_id)
        serializer = PetSerializer(pet)
        return success_response(serializer.data, "Lay chi tiet thu cung thanh cong")

    def put(self, request, pet_id):
        serializer = PetUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pet = PetService.update_pet(request.user, pet_id, serializer.validated_data)
        output = PetSerializer(pet)
        return success_response(output.data, "Cap nhat thu cung thanh cong")

    def delete(self, request, pet_id):
        PetService.delete_pet(request.user, pet_id)
        return success_response(message="Xoa thu cung thanh cong")
