from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from src.common.exceptions import (
    BadRequestException,
    NotFoundException,
    PermissionDeniedException,
    UnauthorizedException,
)
from src.repositories.user_repository import UserRepository


class UserService:
    @staticmethod
    def register_user(validated_data):
        user_data = validated_data.copy()
        password = user_data.pop("password")

        try:
            with transaction.atomic():
                return UserRepository.create_user(password=password, **user_data)
        except IntegrityError as exc:
            raise BadRequestException("Ten dang nhap hoac email da ton tai.") from exc

    @staticmethod
    def login(validated_data):
        username = validated_data["username"]
        password = validated_data["password"]
        user = authenticate(username=username, password=password)

        if not user:
            raise UnauthorizedException("Ten dang nhap hoac mat khau khong chinh xac.")

        if not user.is_active:
            raise UnauthorizedException("Tai khoan da bi khoa.")

        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def logout_user(user_id: int, refresh_token: str):
        try:
            token = RefreshToken(refresh_token)

            if str(token["user_id"]) != str(user_id):
                raise PermissionDeniedException("Ban khong the dang xuat phien cua nguoi dung khac.")

            token.blacklist()
        except TokenError as exc:
            raise BadRequestException("Refresh token khong hop le hoac da het han.") from exc

    @staticmethod
    def refresh_access_token(refresh_token: str):
        try:
            token = RefreshToken(refresh_token)
            return {"access": str(token.access_token)}
        except TokenError as exc:
            raise BadRequestException("Refresh token khong hop le hoac da het han.") from exc

    @staticmethod
    def get_profile(user_id: int):
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Khong tim thay nguoi dung.")
        return user

    @staticmethod
    def update_profile(user_id: int, data):
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Khong tim thay nguoi dung.")

        user.full_name = data.get("full_name", user.full_name)
        user.phone = data.get("phone", user.phone)
        user.address = data.get("address", user.address)
        return UserRepository.save(user)
