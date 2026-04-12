from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from src.common.responses import success_response
from src.serializers.user_serializer import (
    LoginSerializer,
    LogoutSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
    UserSerializer,
)
from src.services.user_service import UserService


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.register_user(serializer.validated_data)
        output = UserSerializer(user)
        return success_response(
            data=output.data,
            message="Dang ky thanh cong.",
            status_code=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = UserService.login(serializer.validated_data)
        output = UserSerializer(result["user"])

        return success_response(
            data={
                "user": output.data,
                "access_token": result["access"],
                "refresh_token": result["refresh"],
            },
            message="Dang nhap thanh cong.",
            status_code=status.HTTP_200_OK,
        )


class RefreshTokenAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = UserService.refresh_access_token(serializer.validated_data["refresh_token"])
        return success_response(
            data={"access_token": result["access"]},
            message="Lam moi access token thanh cong.",
            status_code=status.HTTP_200_OK,
        )


class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        UserService.logout_user(request.user.id, serializer.validated_data["refresh_token"])
        return success_response(
            data=None,
            message="Dang xuat thanh cong.",
            status_code=status.HTTP_200_OK,
        )


class ProfileAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = UserService.get_profile(request.user.id)
        serializer = UserSerializer(user)
        return success_response(
            data=serializer.data,
            message="Lay thong tin ca nhan thanh cong.",
            status_code=status.HTTP_200_OK,
        )

    def put(self, request):
        serializer = UpdateProfileSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        user = UserService.update_profile(request.user.id, serializer.validated_data)
        output = UserSerializer(user)
        return success_response(
            data=output.data,
            message="Cap nhat ho so thanh cong.",
            status_code=status.HTTP_200_OK,
        )
