from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from src.common.exceptions import BusinessException
from src.models import (
    Appointment,
    Clinic,
    MedicalRecord,
    Medicine,
    Pet,
    Prescription,
    PrescriptionItem,
    Service,
    User,
)
from src.services.prescription_service import PrescriptionService


class PrescriptionServiceTests(TestCase):
    # Shared Arrange: a completed visit with prescription and medicine stock.
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="password123",
            full_name="Pet Owner",
        )
        self.clinic = Clinic.objects.create(
            name="Clinic A",
            address="123 Street",
        )
        self.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password123",
            full_name="Clinic Staff",
            role=User.ROLE_CLINIC_STAFF,
            clinic=self.clinic,
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
        self.appointment = Appointment.objects.create(
            owner=self.owner,
            pet=self.pet,
            clinic=self.clinic,
            service=self.service,
            appointment_time=timezone.now() + timedelta(days=1),
            status=Appointment.STATUS_COMPLETED,
        )
        self.medical_record = MedicalRecord.objects.create(
            appointment=self.appointment,
            pet=self.pet,
            clinic=self.clinic,
            staff=self.staff,
            symptoms="Coughing",
            diagnosis="Mild respiratory infection",
        )
        self.prescription = Prescription.objects.create(
            medical_record=self.medical_record,
            clinic=self.clinic,
            staff=self.staff,
        )
        self.medicine = Medicine.objects.create(
            clinic=self.clinic,
            name="Amoxicillin",
            unit="tablet",
            stock_quantity=10,
            price=5000,
        )

    def prescription_item_data(self, quantity=4):
        return {
            "medicine_id": self.medicine.id,
            "quantity": quantity,
            "dosage": "1 tablet",
            "frequency": "Twice daily",
            "duration_days": 5,
            "instruction": "After meal",
        }

    def add_prescription_item(self, quantity=4):
        return PrescriptionService.add_prescription_item(
            self.staff,
            self.prescription.id,
            self.prescription_item_data(quantity=quantity),
        )

    def test_add_prescription_item_decreases_medicine_stock(self):
        # Act
        item = self.add_prescription_item(quantity=4)

        # Assert
        self.medicine.refresh_from_db()

        self.assertEqual(item.quantity, 4)
        self.assertEqual(self.medicine.stock_quantity, 6)

    def test_add_prescription_item_rejects_quantity_greater_than_stock(self):
        # Act / Assert
        with self.assertRaises(BusinessException):
            self.add_prescription_item(quantity=11)

        # Assert
        self.medicine.refresh_from_db()

        self.assertEqual(self.medicine.stock_quantity, 10)
        self.assertEqual(PrescriptionItem.objects.count(), 0)

    def test_add_prescription_item_rejects_duplicate_medicine(self):
        # Arrange
        self.add_prescription_item(quantity=2)

        # Act / Assert
        with self.assertRaises(BusinessException):
            self.add_prescription_item(quantity=2)

        # Assert
        self.medicine.refresh_from_db()

        self.assertEqual(self.medicine.stock_quantity, 8)
        self.assertEqual(PrescriptionItem.objects.count(), 1)

    def test_update_prescription_item_to_higher_quantity_decreases_stock_by_diff(self):
        # Arrange
        item = self.add_prescription_item(quantity=4)

        # Act
        updated_item = PrescriptionService.update_prescription_item(
            self.staff,
            item.id,
            {"quantity": 7},
        )

        # Assert
        self.medicine.refresh_from_db()

        self.assertEqual(updated_item.quantity, 7)
        self.assertEqual(self.medicine.stock_quantity, 3)

    def test_update_prescription_item_to_lower_quantity_returns_stock_by_diff(self):
        # Arrange
        item = self.add_prescription_item(quantity=4)

        # Act
        updated_item = PrescriptionService.update_prescription_item(
            self.staff,
            item.id,
            {"quantity": 2},
        )

        # Assert
        self.medicine.refresh_from_db()

        self.assertEqual(updated_item.quantity, 2)
        self.assertEqual(self.medicine.stock_quantity, 8)

    def test_delete_prescription_item_returns_medicine_stock(self):
        # Arrange
        item = self.add_prescription_item(quantity=4)

        # Act
        PrescriptionService.delete_prescription_item(self.staff, item.id)

        # Assert
        self.medicine.refresh_from_db()

        self.assertEqual(self.medicine.stock_quantity, 10)
        self.assertFalse(PrescriptionItem.objects.filter(id=item.id).exists())
