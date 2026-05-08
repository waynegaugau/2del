from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from src.common.exceptions import (
    BusinessException,
    NotFoundException,
    PermissionDeniedException,
)
from src.models import Appointment, Payment
from src.repositories.payment_repository import PaymentRepository


class PaymentService:
    @staticmethod
    def _validate_owner_payment(user, payment):
        if not payment:
            raise NotFoundException("Không tìm thấy thanh toán.")

        if payment.owner_id != user.id:
            raise PermissionDeniedException("Bạn không có quyền truy cập thanh toán này.")

        return payment

    @staticmethod
    def _get_owner_payment(user, payment_id):
        payment = PaymentRepository.get_by_id(payment_id)
        return PaymentService._validate_owner_payment(user, payment)

    @staticmethod
    def _get_owner_payment_for_update(user, payment_id):
        payment = PaymentRepository.get_by_id_for_update(payment_id)
        return PaymentService._validate_owner_payment(user, payment)

    @staticmethod
    def _calculate_amount(appointment):
        amount = appointment.service.price

        medical_record = getattr(appointment, "medical_record", None)
        if not medical_record:
            return amount

        prescription = getattr(medical_record, "prescription", None)
        if not prescription:
            return amount

        for item in prescription.items.all():
            amount += item.medicine.price * Decimal(item.quantity)

        return amount

    @staticmethod
    def get_user_payments(user):
        return PaymentRepository.get_all_by_owner(user)

    @staticmethod
    def get_payment_detail(user, payment_id):
        return PaymentService._get_owner_payment(user, payment_id)

    @staticmethod
    def create_payment(user, data):
        appointment = PaymentRepository.get_appointment_for_payment(data["appointment_id"])
        if not appointment:
            raise NotFoundException("Không tìm thấy lịch hẹn.")

        if appointment.owner_id != user.id:
            raise PermissionDeniedException("Bạn không có quyền thanh toán lịch hẹn này.")

        if appointment.status != Appointment.STATUS_COMPLETED:
            raise BusinessException("Chỉ có thể thanh toán lịch hẹn đã hoàn tất.")

        existing_payment = PaymentRepository.get_by_appointment_id(appointment.id)
        if existing_payment:
            raise BusinessException("Lịch hẹn này đã có thanh toán.")

        return PaymentRepository.create(
            appointment=appointment,
            owner=appointment.owner,
            clinic=appointment.clinic,
            amount=PaymentService._calculate_amount(appointment),
            method=data.get("method", Payment.METHOD_MOCK_ONLINE),
            status=Payment.STATUS_PENDING,
            note=data.get("note", ""),
        )

    @staticmethod
    def confirm_payment(user, payment_id):
        with transaction.atomic():
            payment = PaymentService._get_owner_payment_for_update(user, payment_id)

            if payment.status == Payment.STATUS_PAID:
                raise BusinessException("Thanh toán này đã hoàn tất.")

            if payment.status != Payment.STATUS_PENDING:
                raise BusinessException("Chỉ có thể xác nhận thanh toán đang chờ xử lý.")

            if payment.method != Payment.METHOD_MOCK_ONLINE:
                raise BusinessException("Chỉ hỗ trợ xác nhận thanh toán online giả lập.")

            payment.status = Payment.STATUS_PAID
            payment.paid_at = timezone.now()
            payment.transaction_code = f"PAY-{payment.id}-{payment.paid_at.strftime('%Y%m%d%H%M%S')}"

            return PaymentRepository.save(payment)
