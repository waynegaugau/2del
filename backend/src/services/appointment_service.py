from datetime import timedelta

from src.models import Appointment, Pet, Clinic, Service
from src.repositories.appointment_repository import AppointmentRepository
from src.common.exceptions import (
    BusinessException,
    NotFoundException,
    PermissionDeniedException,
)


class AppointmentService:
    @staticmethod
    def _has_time_conflict(clinic_id, appointment_time, duration_minutes, exclude_appointment_id=None):
        appointment_end = appointment_time + timedelta(minutes=duration_minutes)
        active_appointments = AppointmentRepository.get_active_by_clinic_id(clinic_id)

        for existing_appointment in active_appointments:
            if exclude_appointment_id and existing_appointment.id == exclude_appointment_id:
                continue

            existing_end = existing_appointment.appointment_time + timedelta(
                minutes=existing_appointment.service.duration_minutes
            )

            if appointment_time < existing_end and existing_appointment.appointment_time < appointment_end:
                return True

        return False

    @staticmethod
    def create_appointment(user, data):
        pet = Pet.objects.filter(id=data["pet_id"], owner=user, is_active=True).first()
        if not pet:
            raise NotFoundException("Khong tim thay thu cung hoac ban khong co quyen su dung.")

        clinic = Clinic.objects.filter(id=data["clinic_id"], is_active=True).first()
        if not clinic:
            raise NotFoundException("Phong kham khong ton tai hoac dang ngung hoat dong.")

        service = Service.objects.filter(
            id=data["service_id"],
            clinic=clinic,
            is_active=True
        ).first()
        if not service:
            raise NotFoundException("Dich vu khong hop le tai phong kham nay.")

        appointment_time = data["appointment_time"]

        if AppointmentService._has_time_conflict(
            clinic.id,
            appointment_time,
            service.duration_minutes,
        ):
            raise BusinessException("Khung gio nay bi trung voi lich hen khac.")

        return AppointmentRepository.create(
            owner=user,
            pet=pet,
            clinic=clinic,
            service=service,
            appointment_time=appointment_time,
            note=data.get("note", ""),
            status=Appointment.STATUS_PENDING,
        )

    @staticmethod
    def get_user_appointments(user):
        return AppointmentRepository.get_all_by_owner(user)

    @staticmethod
    def get_clinic_appointments(user):
        if not user.clinic_id:
            raise BusinessException("Tai khoan staff chua duoc gan phong kham.")

        return AppointmentRepository.get_all_by_clinic_id(user.clinic_id)

    @staticmethod
    def get_clinic_appointment_detail(user, appointment_id):
        if not user.clinic_id:
            raise BusinessException("Tai khoan staff chua duoc gan phong kham.")

        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Khong tim thay lich hen.")

        if user.clinic_id != appointment.clinic_id:
            raise PermissionDeniedException("Ban khong co quyen xem lich hen cua phong kham khac.")

        return appointment

    @staticmethod
    def get_appointment_detail(user, appointment_id):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Khong tim thay lich hen.")

        if appointment.owner != user:
            raise BusinessException("Ban khong co quyen truy cap lich hen nay.")

        return appointment

    @staticmethod
    def update_appointment(user, appointment_id, data):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Khong tim thay lich hen.")

        if appointment.owner != user:
            raise BusinessException("Ban khong co quyen sua lich hen nay.")

        if appointment.status in [
            Appointment.STATUS_CONFIRMED,
            Appointment.STATUS_CHECKED_IN,
            Appointment.STATUS_IN_PROGRESS,
            Appointment.STATUS_COMPLETED,
            Appointment.STATUS_CANCELLED,
            Appointment.STATUS_NO_SHOW,
        ]:
            raise BusinessException("Khong the cap nhat lich hen khi phong kham da tiep nhan xu ly.")

        new_time = data.get("appointment_time")
        if new_time and new_time != appointment.appointment_time:
            if AppointmentService._has_time_conflict(
                appointment.clinic.id,
                new_time,
                appointment.service.duration_minutes,
                exclude_appointment_id=appointment.id,
            ):
                raise BusinessException("Khung gio moi bi trung voi lich hen khac.")
            appointment.appointment_time = new_time

        if "note" in data:
            appointment.note = data["note"]

        return AppointmentRepository.save(appointment)

    @staticmethod
    def cancel_appointment(user, appointment_id):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Khong tim thay lich hen.")

        if appointment.owner != user:
            raise BusinessException("Ban khong co quyen huy lich hen nay.")

        if appointment.status in [
            Appointment.STATUS_CHECKED_IN,
            Appointment.STATUS_IN_PROGRESS,
            Appointment.STATUS_COMPLETED,
            Appointment.STATUS_CANCELLED,
            Appointment.STATUS_NO_SHOW,
        ]:
            raise BusinessException("Khong the huy lich hen o trang thai hien tai.")

        if appointment.status == Appointment.STATUS_CONFIRMED:
            raise BusinessException("Khong the huy lich hen sau khi phong kham da xac nhan.")

        appointment.status = Appointment.STATUS_CANCELLED
        return AppointmentRepository.save(appointment)

    @staticmethod
    def confirm_appointment(user, appointment_id):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Khong tim thay lich hen.")

        if user.clinic_id != appointment.clinic_id:
            raise PermissionDeniedException("Ban khong co quyen xac nhan lich hen cua phong kham khac.")

        if appointment.status != Appointment.STATUS_PENDING:
            raise BusinessException("Chi lich hen dang cho xac nhan moi duoc duyet.")

        appointment.status = Appointment.STATUS_CONFIRMED
        return AppointmentRepository.save(appointment)

    @staticmethod
    def check_in(user, appointment_id):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Khong tim thay lich hen.")

        if user.clinic_id != appointment.clinic_id:
            raise PermissionDeniedException("Ban khong co quyen check-in lich hen cua phong kham khac.")

        if appointment.status != Appointment.STATUS_CONFIRMED:
            raise BusinessException("Chi lich hen da xac nhan moi duoc check-in.")

        appointment.status = Appointment.STATUS_CHECKED_IN
        return AppointmentRepository.save(appointment)

    @staticmethod
    def start_appointment(user, appointment_id):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Khong tim thay lich hen.")

        if user.clinic_id != appointment.clinic_id:
            raise PermissionDeniedException("Ban khong co quyen bat dau kham lich hen cua phong kham khac.")

        if appointment.status != Appointment.STATUS_CHECKED_IN:
            raise BusinessException("Chi lich hen da check-in moi co the bat dau kham.")

        appointment.status = Appointment.STATUS_IN_PROGRESS
        return AppointmentRepository.save(appointment)

    @staticmethod
    def complete_appointment(user, appointment_id):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Khong tim thay lich hen.")

        if user.clinic_id != appointment.clinic_id:
            raise PermissionDeniedException("Ban khong co quyen hoan tat lich hen cua phong kham khac.")

        if appointment.status != Appointment.STATUS_IN_PROGRESS:
            raise BusinessException("Chi lich hen dang kham moi co the hoan tat.")

        appointment.status = Appointment.STATUS_COMPLETED
        return AppointmentRepository.save(appointment)

    @staticmethod
    def mark_no_show(user, appointment_id):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Khong tim thay lich hen.")

        if user.clinic_id != appointment.clinic_id:
            raise PermissionDeniedException("Ban khong co quyen cap nhat lich hen cua phong kham khac.")

        if appointment.status != Appointment.STATUS_CONFIRMED:
            raise BusinessException("Chi lich hen da xac nhan moi co the danh dau vang mat.")

        appointment.status = Appointment.STATUS_NO_SHOW
        return AppointmentRepository.save(appointment)
