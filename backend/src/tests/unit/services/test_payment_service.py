from decimal import Decimal

import pytest

from src.common.exceptions import (
    BusinessException,
    PermissionDeniedException,
)
from src.models import Appointment, Payment
from src.services.payment_service import PaymentService
from src.tests.factories import (
    AppointmentFactory,
    MedicalRecordFactory,
    MedicineFactory,
    PaymentFactory,
    PrescriptionFactory,
    PrescriptionItemFactory,
    ServiceFactory,
    UserFactory,
)


pytestmark = pytest.mark.django_db


def test_create_payment_calculates_service_and_medicine_amount():
    owner = UserFactory()
    service = ServiceFactory(price=Decimal("100000.00"))
    appointment = AppointmentFactory(
        owner=owner,
        clinic=service.clinic,
        service=service,
        status=Appointment.STATUS_COMPLETED,
    )
    record = MedicalRecordFactory(appointment=appointment)
    prescription = PrescriptionFactory(medical_record=record)
    medicine = MedicineFactory(clinic=appointment.clinic, price=Decimal("5000.00"))
    PrescriptionItemFactory(
        prescription=prescription,
        medicine=medicine,
        quantity=2,
    )

    payment = PaymentService.create_payment(
        owner,
        {
            "appointment_id": appointment.id,
            "method": Payment.METHOD_MOCK_ONLINE,
        },
    )

    assert payment.owner == owner
    assert payment.clinic == appointment.clinic
    assert payment.amount == Decimal("110000.00")
    assert payment.status == Payment.STATUS_PENDING


def test_create_payment_rejects_unfinished_appointment():
    owner = UserFactory()
    appointment = AppointmentFactory(owner=owner, status=Appointment.STATUS_PENDING)

    with pytest.raises(BusinessException):
        PaymentService.create_payment(
            owner,
            {
                "appointment_id": appointment.id,
                "method": Payment.METHOD_MOCK_ONLINE,
            },
        )


def test_create_payment_rejects_another_owners_appointment():
    appointment = AppointmentFactory(status=Appointment.STATUS_COMPLETED)
    other_owner = UserFactory()

    with pytest.raises(PermissionDeniedException):
        PaymentService.create_payment(
            other_owner,
            {
                "appointment_id": appointment.id,
                "method": Payment.METHOD_MOCK_ONLINE,
            },
        )


def test_create_payment_rejects_duplicate_payment():
    payment = PaymentFactory()

    with pytest.raises(BusinessException):
        PaymentService.create_payment(
            payment.owner,
            {
                "appointment_id": payment.appointment_id,
                "method": Payment.METHOD_MOCK_ONLINE,
            },
        )


def test_confirm_payment_marks_mock_online_payment_as_paid():
    payment = PaymentFactory(status=Payment.STATUS_PENDING)

    confirmed_payment = PaymentService.confirm_payment(payment.owner, payment.id)

    payment.refresh_from_db()
    assert confirmed_payment.id == payment.id
    assert payment.status == Payment.STATUS_PAID
    assert payment.paid_at is not None
    assert payment.transaction_code.startswith(f"PAY-{payment.id}-")


def test_confirm_payment_rejects_cash_payment():
    payment = PaymentFactory(
        method=Payment.METHOD_CASH,
        status=Payment.STATUS_PENDING,
    )

    with pytest.raises(BusinessException):
        PaymentService.confirm_payment(payment.owner, payment.id)
