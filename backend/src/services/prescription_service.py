from src.repositories.medical_record_repository import MedicalRecordRepository
from src.repositories.medicine_repository import MedicineRepository
from src.repositories.prescription_item_repository import PrescriptionItemRepository
from src.repositories.prescription_repository import PrescriptionRepository
from src.common.exceptions import (
    BusinessException,
    NotFoundException,
    PermissionDeniedException,
)


class PrescriptionService:
    @staticmethod
    def _get_staff_clinic_id(user):
        if not user.clinic_id:
            raise BusinessException("Tai khoan staff chua duoc gan phong kham.")
        return user.clinic_id

    @staticmethod
    def _get_staff_clinic_medical_record(user, medical_record_id):
        clinic_id = PrescriptionService._get_staff_clinic_id(user)

        record = MedicalRecordRepository.get_by_id(medical_record_id)
        if not record:
            raise NotFoundException("Khong tim thay ho so benh an.")

        if record.clinic_id != clinic_id:
            raise PermissionDeniedException("Ban khong co quyen thao tac don thuoc cua phong kham khac.")

        return record

    @staticmethod
    def _get_staff_clinic_prescription(user, prescription_id):
        clinic_id = PrescriptionService._get_staff_clinic_id(user)

        prescription = PrescriptionRepository.get_by_id(prescription_id)
        if not prescription:
            raise NotFoundException("Khong tim thay don thuoc.")

        if prescription.clinic_id != clinic_id:
            raise PermissionDeniedException("Ban khong co quyen thao tac don thuoc cua phong kham khac.")

        return prescription

    @staticmethod
    def _get_staff_clinic_medicine(user, medicine_id):
        clinic_id = PrescriptionService._get_staff_clinic_id(user)

        medicine = MedicineRepository.get_by_id(medicine_id)
        if not medicine:
            raise NotFoundException("Khong tim thay thuoc.")

        if medicine.clinic_id != clinic_id:
            raise PermissionDeniedException("Ban khong co quyen su dung thuoc cua phong kham khac.")

        if not medicine.is_active:
            raise BusinessException("Thuoc nay da ngung hoat dong.")

        return medicine

    @staticmethod
    def create_prescription(user, medical_record_id, data):
        record = PrescriptionService._get_staff_clinic_medical_record(user, medical_record_id)

        existing_prescription = PrescriptionRepository.get_by_medical_record_id(medical_record_id)
        if existing_prescription:
            raise BusinessException("Ho so benh an nay da co don thuoc.")

        return PrescriptionRepository.create(
            medical_record=record,
            clinic=record.clinic,
            staff=user,
            note=data.get("note", ""),
        )

    @staticmethod
    def get_prescription_by_medical_record(user, medical_record_id):
        PrescriptionService._get_staff_clinic_medical_record(user, medical_record_id)

        prescription = PrescriptionRepository.get_by_medical_record_id(medical_record_id)
        if not prescription:
            raise NotFoundException("Khong tim thay don thuoc.")

        return prescription

    @staticmethod
    def get_prescription_detail(user, prescription_id):
        return PrescriptionService._get_staff_clinic_prescription(user, prescription_id)

    @staticmethod
    def update_prescription(user, prescription_id, data):
        prescription = PrescriptionService._get_staff_clinic_prescription(user, prescription_id)

        if "note" in data:
            prescription.note = data["note"]

        return PrescriptionRepository.save(prescription)

    @staticmethod
    def add_prescription_item(user, prescription_id, data):
        prescription = PrescriptionService._get_staff_clinic_prescription(user, prescription_id)
        medicine = PrescriptionService._get_staff_clinic_medicine(user, data["medicine_id"])

        if medicine.stock_quantity < data["quantity"]:
            raise BusinessException("So luong thuoc ton kho khong du.")

        existing_item = PrescriptionItemRepository.get_by_prescription_and_medicine(
            prescription.id,
            medicine.id,
        )
        if existing_item:
            raise BusinessException("Thuoc nay da ton tai trong don thuoc.")

        item = PrescriptionItemRepository.create(
            prescription=prescription,
            medicine=medicine,
            quantity=data["quantity"],
            dosage=data["dosage"],
            frequency=data["frequency"],
            duration_days=data["duration_days"],
            instruction=data.get("instruction", ""),
        )

        medicine.stock_quantity -= data["quantity"]
        MedicineRepository.save(medicine)
        return item

    @staticmethod
    def update_prescription_item(user, item_id, data):
        item = PrescriptionItemRepository.get_by_id(item_id)
        if not item:
            raise NotFoundException("Khong tim thay chi tiet don thuoc.")

        prescription = PrescriptionService._get_staff_clinic_prescription(user, item.prescription_id)
        medicine = item.medicine

        new_quantity = data.get("quantity", item.quantity)
        quantity_diff = new_quantity - item.quantity

        if quantity_diff > 0 and medicine.stock_quantity < quantity_diff:
            raise BusinessException("So luong thuoc ton kho khong du.")

        if quantity_diff != 0:
            medicine.stock_quantity -= quantity_diff
            MedicineRepository.save(medicine)

        item.quantity = new_quantity

        if "dosage" in data:
            item.dosage = data["dosage"]
        if "frequency" in data:
            item.frequency = data["frequency"]
        if "duration_days" in data:
            item.duration_days = data["duration_days"]
        if "instruction" in data:
            item.instruction = data["instruction"]

        return PrescriptionItemRepository.save(item)

    @staticmethod
    def delete_prescription_item(user, item_id):
        item = PrescriptionItemRepository.get_by_id(item_id)
        if not item:
            raise NotFoundException("Khong tim thay chi tiet don thuoc.")

        PrescriptionService._get_staff_clinic_prescription(user, item.prescription_id)

        medicine = item.medicine
        medicine.stock_quantity += item.quantity
        MedicineRepository.save(medicine)

        PrescriptionItemRepository.delete(item)
