from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from src.models import User


class UserSerializer(serializers.ModelSerializer):
    clinic_id = serializers.IntegerField(source="clinic.id", read_only=True)
    clinic_name = serializers.CharField(source="clinic.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "phone",
            "address",
            "role",
            "clinic_id",
            "clinic_name",
            "is_active",
            "created_at",
            "updated_at",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        error_messages={
            "min_length": "Mat khau phai co it nhat 6 ky tu.",
            "blank": "Mat khau khong duoc de trong.",
        },
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "full_name",
            "phone",
            "address",
        ]

    def validate(self, attrs):
        user = User(
            username=attrs.get("username"),
            email=attrs.get("email"),
            full_name=attrs.get("full_name"),
        )

        try:
            validate_password(attrs["password"], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc

        return attrs

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ten dang nhap da ton tai.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email da ton tai.")
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["full_name", "phone", "address"]
