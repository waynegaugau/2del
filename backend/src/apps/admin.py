from django.contrib import admin
from django.utils.html import format_html

from .models import (
    User, Clinic, Staff, Service, Pet, Appointment,
    MedicalRecord, Medication, Prescription, Payment
)


# Inlines
class StaffInline(admin.TabularInline):
    model = Staff
    extra = 0


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1


# User Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email', 'phone']


# Clinic Admin (CRUD Phòng khám)
@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'owner', 'created_at']
    inlines = [StaffInline, ServiceInline]  # ✅ Inline nhân viên/dịch vụ
    search_fields = ['name']


# Staff Admin (Quản lý nhân viên)
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'clinic', 'role', 'is_active']
    list_filter = ['role', 'clinic', 'is_active']
    search_fields = ['user__username']


# Service Admin (Dịch vụ)
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'clinic', 'category', 'price', 'is_active']
    list_filter = ['category', 'clinic']
    list_editable = ['is_active']
    search_fields = ['name']


# Các model khác (riêng lẻ)
@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'species']
    list_filter = ['species']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['pet', 'clinic', 'appointment_date', 'status']
    list_filter = ['status', 'appointment_date']
    list_editable = ['status']


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['pet', 'clinic', 'created_at']
    list_filter = ['created_at']


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'stock_quantity', 'price_per_unit']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['medication', 'quantity_prescribed']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'amount', 'status']


# Site title
admin.site.site_header = "🏥 Pet Clinic Admin"