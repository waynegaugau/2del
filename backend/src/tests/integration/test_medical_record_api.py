from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from src.models import Appointment, Clinic, MedicalRecord, Pet, Service, User


class MedicalRecordAPITests(TestCase):
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

    def medical_record_payload(self):
        return {
            "symptoms": "Coughing",
            "diagnosis": "Mild respiratory infection",
            "treatment": "Rest and medication",
            "note": "Follow up in 7 days",
        }

    def create_appointment(self, owner=None, pet=None, status_value=Appointment.STATUS_CHECKED_IN):
        return Appointment.objects.create(
            owner=owner or self.owner,
            pet=pet or self.pet,
            clinic=self.clinic,
            service=self.service,
            appointment_time=timezone.now() + timedelta(days=1),
            status=status_value,
        )

    def create_medical_record(self, owner=None, pet=None):
        appointment = self.create_appointment(owner=owner, pet=pet)
        return MedicalRecord.objects.create(
            appointment=appointment,
            pet=appointment.pet,
            clinic=appointment.clinic,
            staff=self.staff,
            symptoms="Coughing",
            diagnosis="Mild respiratory infection",
            treatment="Rest",
            note="",
        )

    def test_staff_can_create_medical_record_for_checked_in_appointment(self):
        # Arrange
        appointment = self.create_appointment(status_value=Appointment.STATUS_CHECKED_IN)
        self.authenticate(self.staff)

        # Act
        response = self.client.post(
            reverse("appointment-medical-record", kwargs={"appointment_id": appointment.id}),
            self.medical_record_payload(),
            format="json",
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["appointment_id"], appointment.id)
        self.assertEqual(response.data["data"]["pet_id"], self.pet.id)
        self.assertEqual(response.data["data"]["clinic_id"], self.clinic.id)
        self.assertEqual(response.data["data"]["staff_id"], self.staff.id)
        self.assertEqual(MedicalRecord.objects.count(), 1)

    def test_staff_cannot_create_medical_record_for_pending_appointment(self):
        # Arrange
        appointment = self.create_appointment(status_value=Appointment.STATUS_PENDING)
        self.authenticate(self.staff)

        # Act
        response = self.client.post(
            reverse("appointment-medical-record", kwargs={"appointment_id": appointment.id}),
            self.medical_record_payload(),
            format="json",
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(MedicalRecord.objects.count(), 0)

    def test_staff_from_other_clinic_cannot_create_medical_record(self):
        # Arrange
        appointment = self.create_appointment(status_value=Appointment.STATUS_CHECKED_IN)
        self.authenticate(self.other_staff)

        # Act
        response = self.client.post(
            reverse("appointment-medical-record", kwargs={"appointment_id": appointment.id}),
            self.medical_record_payload(),
            format="json",
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])
        self.assertEqual(MedicalRecord.objects.count(), 0)

    def test_pet_owner_can_list_medical_records_for_their_pet(self):
        # Arrange
        record = self.create_medical_record()
        self.create_medical_record(owner=self.other_owner, pet=self.other_pet)
        self.authenticate(self.owner)

        # Act
        response = self.client.get(
            reverse("owner-pet-medical-record-list", kwargs={"pet_id": self.pet.id}),
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["id"], record.id)

    def test_pet_owner_cannot_get_medical_record_detail_for_another_owner_pet(self):
        # Arrange
        record = self.create_medical_record(owner=self.other_owner, pet=self.other_pet)
        self.authenticate(self.owner)

        # Act
        response = self.client.get(
            reverse("owner-medical-record-detail", kwargs={"record_id": record.id}),
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])
