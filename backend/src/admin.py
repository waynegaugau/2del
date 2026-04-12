from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from src.models import (
    User,
    Clinic,
    Pet,
    Service,
    Appointment,
    MedicalRecord,
    Medicine,
    Prescription,
    PrescriptionItem,
)


class CustomUserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        clinic = cleaned_data.get("clinic")

        if role == User.ROLE_CLINIC_STAFF and not clinic:
            raise ValidationError("Nhân viên phòng khám bắt buộc phải thuộc một phòng khám.")

        if role in [User.ROLE_PET_OWNER, User.ROLE_ADMIN] and clinic is not None:
            raise ValidationError("Chỉ nhân viên phòng khám mới được phép thuộc một phòng khám.")

        return cleaned_data


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserAdminForm

    list_display = (
        "id",
        "username",
        "email",
        "full_name",
        "role",
        "clinic",
        "is_active",
        "is_staff",
        "created_at",
    )
    list_filter = ("role", "is_active", "clinic")
    search_fields = ("username", "email", "full_name", "phone")
    ordering = ("-id",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Thông tin bổ sung", {
            "fields": ("full_name", "phone", "address", "role", "clinic")
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Thông tin bổ sung", {
            "fields": ("full_name", "email", "phone", "address", "role", "clinic")
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.role == User.ROLE_ADMIN:
            obj.is_staff = True
            obj.is_superuser = True
        else:
            obj.is_staff = False
            obj.is_superuser = False

        super().save_model(request, obj, form, change)


class SoftDeleteAdminMixin:
    actions = None

    def delete_model(self, request, obj):
        obj.is_active = False
        obj.save(update_fields=["is_active", "updated_at"])

    def delete_queryset(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(Clinic)
class ClinicAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("id", "name", "phone", "email", "is_active", "created_at")
    search_fields = ("name", "phone", "email")
    list_filter = ("is_active",)


@admin.register(Pet)
class PetAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("id", "name", "species", "breed", "owner", "is_active", "created_at")
    search_fields = ("name", "species", "breed", "owner__username", "owner__full_name")
    list_filter = ("species", "is_active")


@admin.register(Service)
class ServiceAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("id", "name", "clinic", "price", "duration_minutes", "is_active", "created_at")
    search_fields = ("name", "clinic__name")
    list_filter = ("clinic", "is_active")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "pet", "clinic", "service", "appointment_time", "status", "created_at")
    search_fields = ("pet__name", "clinic__name", "service__name")
    list_filter = ("status", "clinic", "appointment_time")
    readonly_fields = (
        "owner",
        "pet",
        "clinic",
        "service",
        "appointment_time",
        "note",
        "status",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "appointment", "pet", "clinic", "staff", "created_at")
    search_fields = (
        "appointment__id",
        "pet__name",
        "clinic__name",
        "staff__username",
        "staff__full_name",
    )
    list_filter = ("clinic", "staff", "created_at")
    readonly_fields = (
        "appointment",
        "pet",
        "clinic",
        "staff",
        "symptoms",
        "diagnosis",
        "treatment",
        "note",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Medicine)
class MedicineAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("id", "name", "clinic", "unit", "stock_quantity", "price", "is_active", "created_at")
    search_fields = ("name", "clinic__name", "unit")
    list_filter = ("clinic", "is_active")


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "medical_record", "clinic", "staff", "created_at")
    search_fields = (
        "medical_record__id",
        "clinic__name",
        "staff__username",
        "staff__full_name",
    )
    list_filter = ("clinic", "staff", "created_at")
    readonly_fields = (
        "medical_record",
        "clinic",
        "staff",
        "note",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ("id", "prescription", "medicine", "quantity", "duration_days", "created_at")
    search_fields = (
        "prescription__id",
        "medicine__name",
        "medicine__clinic__name",
    )
    list_filter = ("medicine__clinic", "created_at")
    readonly_fields = (
        "prescription",
        "medicine",
        "quantity",
        "dosage",
        "frequency",
        "duration_days",
        "instruction",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
