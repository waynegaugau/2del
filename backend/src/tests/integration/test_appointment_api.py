from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from src.models import Appointment, Clinic, Pet, Service, User


class AppointmentAPITests(TestCase):
    # Shared Arrange: API client, users, clinics, service, and pets.
    def setUp(self):
        self.client = APIClient()
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

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def appointment_payload(self, appointment_time=None):
        return {
            "pet_id": self.pet.id,
            "clinic_id": self.clinic.id,
            "service_id": self.service.id,
            "appointment_time": appointment_time or timezone.now() + timedelta(days=1),
            "note": "Regular checkup",
        }

    def create_appointment(self, owner=None, pet=None, appointment_time=None):
        return Appointment.objects.create(
            owner=owner or self.owner,
            pet=pet or self.pet,
            clinic=self.clinic,
            service=self.service,
            appointment_time=appointment_time or timezone.now() + timedelta(days=1),
            status=Appointment.STATUS_PENDING,
        )

    def test_pet_owner_can_create_appointment(self):
        # Arrange
        self.authenticate(self.owner)

        # Act
        response = self.client.post(
            reverse("appointment-list-create"),
            self.appointment_payload(),
            format="json",
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["owner"], self.owner.id)
        self.assertEqual(response.data["data"]["pet"], self.pet.id)
        self.assertEqual(response.data["data"]["status"], Appointment.STATUS_PENDING)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_pet_owner_cannot_create_appointment_with_time_conflict(self):
        # Arrange
        appointment_time = timezone.now() + timedelta(days=1)
        self.create_appointment(appointment_time=appointment_time)
        self.authenticate(self.owner)

        # Act
        response = self.client.post(
            reverse("appointment-list-create"),
            self.appointment_payload(
                appointment_time=appointment_time + timedelta(minutes=30),
            ),
            format="json",
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(Appointment.objects.count(), 1)

    def test_staff_can_confirm_appointment_in_same_clinic(self):
        # Arrange
        appointment = self.create_appointment()
        self.authenticate(self.staff)

        # Act
        response = self.client.post(
            reverse("appointment-confirm", kwargs={"appointment_id": appointment.id}),
            format="json",
        )

        # Assert
        appointment.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["status"], Appointment.STATUS_CONFIRMED)
        self.assertEqual(appointment.status, Appointment.STATUS_CONFIRMED)

    def test_staff_from_other_clinic_cannot_confirm_appointment(self):
        # Arrange
        appointment = self.create_appointment()
        self.authenticate(self.other_staff)

        # Act
        response = self.client.post(
            reverse("appointment-confirm", kwargs={"appointment_id": appointment.id}),
            format="json",
        )

        # Assert
        appointment.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])
        self.assertEqual(appointment.status, Appointment.STATUS_PENDING)

    def test_pet_owner_can_list_only_their_appointments(self):
        # Arrange
        owner_appointment = self.create_appointment()
        self.create_appointment(owner=self.other_owner, pet=self.other_pet)
        self.authenticate(self.owner)

        # Act
        response = self.client.get(reverse("appointment-list-create"))

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["id"], owner_appointment.id)
