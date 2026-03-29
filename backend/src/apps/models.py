from django.db import models
from django.contrib.auth.models import AbstractUser
 
 
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        STAFF = 'staff', 'Phòng khám / Groomer'
        OWNER = 'owner', 'Chủ thú cưng'
 
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.OWNER)
 
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
 
    def is_admin(self):
        return self.role == self.Role.ADMIN
 
    def is_clinic_staff(self):  # đổi từ is_staff_member để tránh nhầm với Django built-in
        return self.role == self.Role.STAFF
 
    def is_owner(self):
        return self.role == self.Role.OWNER
 
 
class Clinic(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clinics',
        # bỏ limit_choices_to — validation để ở serializer
    )
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return self.name
 
 
class Staff(models.Model):
    class StaffRole(models.TextChoices):
        DOCTOR = 'doctor', 'Bác sĩ'
        NURSE = 'nurse', 'Y tá'
        GROOMER = 'groomer', 'Groomer'
        RECEPTIONIST = 'receptionist', 'Lễ tân'
 
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='staff_members'
    )
    role = models.CharField(max_length=20, choices=StaffRole.choices)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
 
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"
 
 
class Service(models.Model):
    class Category(models.TextChoices):
        MEDICAL = 'medical', 'Khám & Điều trị'
        GROOMING = 'grooming', 'Grooming'
        VACCINE = 'vaccine', 'Tiêm phòng'
        OTHER = 'other', 'Khác'
 
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='services'
    )
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
 
    def __str__(self):
        return f"{self.name} - {self.clinic.name}"
 
 
class Pet(models.Model):
    class Gender(models.TextChoices):
        MALE = 'male', 'Đực'
        FEMALE = 'female', 'Cái'
        UNKNOWN = 'unknown', 'Không rõ'
 
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pets',
        # bỏ limit_choices_to — validation để ở serializer
    )
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)
    breed = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.UNKNOWN)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
 
    def __str__(self):
        return f"{self.name} ({self.owner.username})"
 
 
class VaccinationRecord(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='vaccinations')
    vaccine_name = models.CharField(max_length=255)
    administered_date = models.DateField()
    next_due_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
 
    def __str__(self):
        return f"{self.vaccine_name} - {self.pet.name} ({self.administered_date})"
 
 
class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Chờ xác nhận'
        CONFIRMED = 'confirmed', 'Đã xác nhận'
        CHECKED_IN = 'checked_in', 'Đã check-in'
        CANCELLED = 'cancelled', 'Đã huỷ'
        COMPLETED = 'completed', 'Hoàn thành'
 
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='appointments')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='appointments')
    staff = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        related_name='appointments'
    )
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['staff', 'appointment_date'],
                condition=models.Q(staff__isnull=False),  # fix: bỏ qua khi staff=null
                name='unique_staff_appointment_slot'
            )
        ]
 
    def __str__(self):
        return f"Lịch hẹn #{self.id} - {self.pet.name} ({self.appointment_date.date()})"
 
    def check_in(self):
        if self.status == self.Status.CONFIRMED:
            self.status = self.Status.CHECKED_IN
            self.save()
 
 
class MedicalRecord(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='medical_records')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medical_record'
    )
    diagnosis = models.TextField()
    treatment_plan = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return f"Bệnh án - {self.pet.name} ({self.created_at.date()})"
 
 
class Medication(models.Model):
    name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    unit = models.CharField(max_length=50)
    stock_quantity = models.PositiveIntegerField(default=0)
    min_stock_level = models.PositiveIntegerField(default=5)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
 
    def __str__(self):
        return f"{self.name} ({self.stock_quantity} {self.unit} còn lại)"
 
    def is_running_low(self):
        return self.stock_quantity <= self.min_stock_level
 
 
class Prescription(models.Model):
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    medication = models.ForeignKey(
        Medication,
        on_delete=models.PROTECT,
        related_name='prescribed_history'
    )
    quantity_prescribed = models.PositiveIntegerField()
    dosage = models.CharField(max_length=255)
    instructions = models.TextField(blank=True, null=True)
    duration = models.CharField(max_length=100)
 
    def __str__(self):
        return f"{self.medication.name} - {self.medical_record.pet.name}"
 
 
class Payment(models.Model):
    class Status(models.TextChoices):
        UNPAID = 'unpaid', 'Chưa thanh toán'
        PAID = 'paid', 'Đã thanh toán'
        REFUNDED = 'refunded', 'Đã hoàn tiền'
 
    class Method(models.TextChoices):
        CASH = 'cash', 'Tiền mặt'
        CARD = 'card', 'Thẻ ngân hàng'
        TRANSFER = 'transfer', 'Chuyển khoản'
 
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=Method.choices,
        blank=True,
        null=True
    )
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.UNPAID)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
 
    def __str__(self):
        return f"Thanh toán #{self.id} - {self.get_status_display()}"