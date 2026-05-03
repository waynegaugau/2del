from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from src.common.exceptions import BusinessException, PermissionDeniedException
from src.models import Appointment, Clinic, MedicalRecord, Pet, Service, User
from src.services.medical_record_service import MedicalRecordService


class MedicalRecordServiceTests(TestCase):
    # Shared Arrange: owners, staff users, clinics, service, and pets.
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

    def medical_record_data(self):
        return {
            "symptoms": "Coughing",
            "diagnosis": "Mild respiratory infection",
            "treatment": "Rest and medication",
            "note": "Follow up in 7 days",
        }

    def create_appointment(self, owner=None, pet=None, status=Appointment.STATUS_CHECKED_IN):
        return Appointment.objects.create(
            owner=owner or self.owner,
            pet=pet or self.pet,
            clinic=self.clinic,
            service=self.service,
            appointment_time=timezone.now() + timedelta(days=1),
            status=status,
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
        appointment = self.create_appointment(status=Appointment.STATUS_CHECKED_IN)

        # Act
        record = MedicalRecordService.create_medical_record(
            self.staff,
            appointment.id,
            self.medical_record_data(),
        )

        # Assert
        self.assertEqual(record.appointment, appointment)
        self.assertEqual(record.pet, self.pet)
        self.assertEqual(record.clinic, self.clinic)
        self.assertEqual(record.staff, self.staff)
        self.assertEqual(record.symptoms, "Coughing")
        self.assertEqual(record.diagnosis, "Mild respiratory infection")

    def test_create_medical_record_rejects_pending_appointment(self):
        # Arrange
        appointment = self.create_appointment(status=Appointment.STATUS_PENDING)

        # Act / Assert
        with self.assertRaises(BusinessException):
            MedicalRecordService.create_medical_record(
                self.staff,
                appointment.id,
                self.medical_record_data(),
            )

        # Assert
        self.assertEqual(MedicalRecord.objects.count(), 0)

    def test_create_medical_record_rejects_duplicate_for_same_appointment(self):
        # Arrange
        appointment = self.create_appointment(status=Appointment.STATUS_CHECKED_IN)
        MedicalRecordService.create_medical_record(
            self.staff,
            appointment.id,
            self.medical_record_data(),
        )

        # Act / Assert
        with self.assertRaises(BusinessException):
            MedicalRecordService.create_medical_record(
                self.staff,
                appointment.id,
                self.medical_record_data(),
            )

        # Assert
        self.assertEqual(MedicalRecord.objects.count(), 1)

    def test_staff_from_other_clinic_cannot_create_medical_record(self):
        # Arrange
        appointment = self.create_appointment(status=Appointment.STATUS_CHECKED_IN)

        # Act / Assert
        with self.assertRaises(PermissionDeniedException):
            MedicalRecordService.create_medical_record(
                self.other_staff,
                appointment.id,
                self.medical_record_data(),
            )

        # Assert
        self.assertEqual(MedicalRecord.objects.count(), 0)

    def test_owner_can_get_medical_records_for_their_pet(self):
        # Arrange
        record = self.create_medical_record()

        # Act
        records = MedicalRecordService.get_pet_owner_medical_records(
            self.owner,
            self.pet.id,
        )

        # Assert
        self.assertEqual(list(records), [record])

    def test_owner_cannot_get_medical_record_detail_for_another_owner_pet(self):
        # Arrange
        record = self.create_medical_record(owner=self.other_owner, pet=self.other_pet)

        # Act / Assert
        with self.assertRaises(PermissionDeniedException):
            MedicalRecordService.get_pet_owner_medical_record_detail(
                self.owner,
                record.id,
            )

    def test_staff_can_update_medical_record_in_same_clinic(self):
        # Arrange
        record = self.create_medical_record()

        # Act
        updated_record = MedicalRecordService.update_medical_record(
            self.staff,
            record.id,
            {
                "symptoms": "Fever",
                "diagnosis": "Viral infection",
                "treatment": "Hydration",
                "note": "Monitor temperature",
            },
        )

        # Assert
        self.assertEqual(updated_record.symptoms, "Fever")
        self.assertEqual(updated_record.diagnosis, "Viral infection")
        self.assertEqual(updated_record.treatment, "Hydration")
        self.assertEqual(updated_record.note, "Monitor temperature")

    def test_staff_from_other_clinic_cannot_update_medical_record(self):
        # Arrange
        record = self.create_medical_record()

        # Act / Assert
        with self.assertRaises(PermissionDeniedException):
            MedicalRecordService.update_medical_record(
                self.other_staff,
                record.id,
                {"diagnosis": "Updated diagnosis"},
            )
