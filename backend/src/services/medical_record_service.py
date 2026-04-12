from src.models import Appointment
from src.repositories.appointment_repository import AppointmentRepository
from src.repositories.medical_record_repository import MedicalRecordRepository
from src.repositories.pet_repository import PetRepository
from src.common.exceptions import (
    BusinessException,
    NotFoundException,
    PermissionDeniedException,
)


class MedicalRecordService:
    ALLOWED_APPOINTMENT_STATUSES = {
        Appointment.STATUS_CHECKED_IN,
        Appointment.STATUS_IN_PROGRESS,
        Appointment.STATUS_COMPLETED,
    }

    @staticmethod
    def _get_staff_clinic_appointment(user, appointment_id):
        if not user.clinic_id:
            raise BusinessException("Tai khoan staff chua duoc gan phong kham.")

        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Khong tim thay lich hen.")

        if user.clinic_id != appointment.clinic_id:
            raise PermissionDeniedException("Ban khong co quyen thao tac ho so benh an cua phong kham khac.")

        if appointment.status not in MedicalRecordService.ALLOWED_APPOINTMENT_STATUSES:
            raise BusinessException("Chi duoc tao ho so benh an khi lich hen da check-in, dang kham hoac da hoan tat.")

        return appointment

    @staticmethod
    def create_medical_record(user, appointment_id, data):
        appointment = MedicalRecordService._get_staff_clinic_appointment(user, appointment_id)

        existing_record = MedicalRecordRepository.get_by_appointment_id(appointment_id)
        if existing_record:
            raise BusinessException("Lich hen nay da co ho so benh an.")

        return MedicalRecordRepository.create(
            appointment=appointment,
            pet=appointment.pet,
            clinic=appointment.clinic,
            staff=user,
            symptoms=data["symptoms"],
            diagnosis=data["diagnosis"],
            treatment=data.get("treatment", ""),
            note=data.get("note", ""),
        )

    @staticmethod
    def get_medical_record_by_appointment(user, appointment_id):
        MedicalRecordService._get_staff_clinic_appointment(user, appointment_id)

        record = MedicalRecordRepository.get_by_appointment_id(appointment_id)
        if not record:
            raise NotFoundException("Khong tim thay ho so benh an.")

        return record

    @staticmethod
    def get_medical_record_detail(user, record_id):
        record = MedicalRecordRepository.get_by_id(record_id)
        if not record:
            raise NotFoundException("Khong tim thay ho so benh an.")

        if not user.clinic_id:
            raise BusinessException("Tai khoan staff chua duoc gan phong kham.")

        if user.clinic_id != record.clinic_id:
            raise PermissionDeniedException("Ban khong co quyen xem ho so benh an cua phong kham khac.")

        return record

    @staticmethod
    def get_pet_medical_records(user, pet_id):
        if not user.clinic_id:
            raise BusinessException("Tai khoan staff chua duoc gan phong kham.")

        pet = PetRepository.get_by_id_including_inactive(pet_id)
        if not pet:
            raise NotFoundException("Khong tim thay thu cung.")

        return MedicalRecordRepository.get_by_pet_id_and_clinic_id(pet_id, user.clinic_id)

    @staticmethod
    def update_medical_record(user, record_id, data):
        record = MedicalRecordService.get_medical_record_detail(user, record_id)

        for field in ["symptoms", "diagnosis", "treatment", "note"]:
            if field in data:
                setattr(record, field, data[field])

        return MedicalRecordRepository.save(record)
