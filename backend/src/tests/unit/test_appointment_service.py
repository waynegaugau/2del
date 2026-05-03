from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from src.common.exceptions import (
    BusinessException,
    NotFoundException,
    PermissionDeniedException,
)
from src.models import Appointment, Clinic, Pet, Service, User
from src.services.appointment_service import AppointmentService


class AppointmentServiceTests(TestCase):
    # Shared Arrange: common users, clinics, service, and pets.
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="password123",
            full_name="Pet Owner",
        )
        self.other_owner = User.objects.create_user(
            username="other_owner",
            email="other-owner@example.com",
            password="password123",
            full_name="Other Owner",
        )
        self.clinic = Clinic.objects.create(
            name="Clinic A",
            address="123 Street",
        )
        self.other_clinic = Clinic.objects.create(
            name="Clinic B",
            address="456 Street",
        )
        self.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password123",
            full_name="Clinic Staff",
            role=User.ROLE_CLINIC_STAFF,
            clinic=self.clinic,
        )
        self.other_staff = User.objects.create_user(
            username="other_staff",
            email="other-staff@example.com",
            password="password123",
            full_name="Other Clinic Staff",
            role=User.ROLE_CLINIC_STAFF,
            clinic=self.other_clinic,
        )
        self.service = Service.objects.create(
            clinic=self.clinic,
            name="General Exam",
            service_type=Service.SERVICE_EXAM,
            price=100000,
            duration_minutes=60,
        )
        self.pet = Pet.objects.create(
            owner=self.owner,
            name="Milu",
            species=Pet.SPECIES_DOG,
            gender=Pet.GENDER_MALE,
        )
        self.other_pet = Pet.objects.create(
            owner=self.other_owner,
            name="Mina",
            species=Pet.SPECIES_CAT,
            gender=Pet.GENDER_FEMALE,
        )

    def appointment_data(self, appointment_time=None, pet_id=None):
        return {
            "pet_id": pet_id or self.pet.id,
            "clinic_id": self.clinic.id,
            "service_id": self.service.id,
            "appointment_time": appointment_time or timezone.now() + timedelta(days=1),
            "note": "Regular checkup",
        }

    def create_pending_appointment(self, appointment_time=None):
        return Appointment.objects.create(
            owner=self.owner,
            pet=self.pet,
            clinic=self.clinic,
            service=self.service,
            appointment_time=appointment_time or timezone.now() + timedelta(days=1),
            status=Appointment.STATUS_PENDING,
        )

    def test_create_appointment_success(self):
        # Arrange
        appointment_time = timezone.now() + timedelta(days=1)

        # Act
        appointment = AppointmentService.create_appointment(
            self.owner,
            self.appointment_data(appointment_time=appointment_time),
        )

        # Assert
        self.assertEqual(appointment.owner, self.owner)
        self.assertEqual(appointment.pet, self.pet)
        self.assertEqual(appointment.clinic, self.clinic)
        self.assertEqual(appointment.service, self.service)
        self.assertEqual(appointment.appointment_time, appointment_time)
        self.assertEqual(appointment.status, Appointment.STATUS_PENDING)

    def test_create_appointment_rejects_pet_from_another_owner(self):
        # Act / Assert
        with self.assertRaises(NotFoundException):
            AppointmentService.create_appointment(
                self.owner,
                self.appointment_data(pet_id=self.other_pet.id),
            )

    def test_create_appointment_rejects_overlapping_time_slot(self):
        # Arrange
        appointment_time = timezone.now() + timedelta(days=1)
        self.create_pending_appointment(appointment_time=appointment_time)

        # Act / Assert
        with self.assertRaises(BusinessException):
            AppointmentService.create_appointment(
                self.owner,
                self.appointment_data(
                    appointment_time=appointment_time + timedelta(minutes=30),
                ),
            )

    def test_staff_can_move_appointment_through_service_flow(self):
        # Arrange
        appointment = self.create_pending_appointment()

        # Act / Assert
        appointment = AppointmentService.confirm_appointment(self.staff, appointment.id)
        self.assertEqual(appointment.status, Appointment.STATUS_CONFIRMED)

        appointment = AppointmentService.check_in(self.staff, appointment.id)
        self.assertEqual(appointment.status, Appointment.STATUS_CHECKED_IN)

        appointment = AppointmentService.start_appointment(self.staff, appointment.id)
        self.assertEqual(appointment.status, Appointment.STATUS_IN_PROGRESS)

        appointment = AppointmentService.complete_appointment(self.staff, appointment.id)
        self.assertEqual(appointment.status, Appointment.STATUS_COMPLETED)

    def test_staff_from_other_clinic_cannot_confirm_appointment(self):
        # Arrange
        appointment = self.create_pending_appointment()

        # Act / Assert
        with self.assertRaises(PermissionDeniedException):
            AppointmentService.confirm_appointment(self.other_staff, appointment.id)

    def test_staff_from_other_clinic_cannot_check_in_appointment(self):
        # Arrange
        appointment = self.create_pending_appointment()
        appointment.status = Appointment.STATUS_CONFIRMED
        appointment.save()

        # Act / Assert
        with self.assertRaises(PermissionDeniedException):
            AppointmentService.check_in(self.other_staff, appointment.id)

    def test_check_in_requires_confirmed_appointment(self):
        # Arrange
        appointment = self.create_pending_appointment()

        # Act / Assert
        with self.assertRaises(BusinessException):
            AppointmentService.check_in(self.staff, appointment.id)

    def test_owner_cannot_update_confirmed_appointment(self):
        # Arrange
        appointment = self.create_pending_appointment()
        appointment.status = Appointment.STATUS_CONFIRMED
        appointment.save()

        # Act / Assert
        with self.assertRaises(BusinessException):
            AppointmentService.update_appointment(
                self.owner,
                appointment.id,
                {"note": "Updated note"},
            )

    def test_owner_cannot_cancel_confirmed_appointment(self):
        # Arrange
        appointment = self.create_pending_appointment()
        appointment.status = Appointment.STATUS_CONFIRMED
        appointment.save()

        # Act / Assert
        with self.assertRaises(BusinessException):
            AppointmentService.cancel_appointment(self.owner, appointment.id)
