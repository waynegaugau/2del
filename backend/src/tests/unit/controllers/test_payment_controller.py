import pytest
from rest_framework import status

from src.controllers.payment_controller import (
    PaymentConfirmAPIView,
    PaymentDetailAPIView,
    PaymentListCreateAPIView,
)
from src.models import Payment
from src.tests.factories import PaymentFactory
from src.tests.unit.controllers.helpers import assert_success, make_request


pytestmark = pytest.mark.django_db


def test_payment_controller_delegates_payment_flows(mocker):
    payment = PaymentFactory()

    get_payments = mocker.patch(
        "src.controllers.payment_controller.PaymentService.get_user_payments",
        return_value=[payment],
    )
    assert_success(PaymentListCreateAPIView().get(make_request(payment.owner)))
    get_payments.assert_called_once_with(payment.owner)

    create_payment = mocker.patch(
        "src.controllers.payment_controller.PaymentService.create_payment",
        return_value=payment,
    )
    assert_success(
        PaymentListCreateAPIView().post(
            make_request(
                payment.owner,
                {
                    "appointment_id": payment.appointment_id,
                    "method": Payment.METHOD_MOCK_ONLINE,
                },
            ),
        ),
        status.HTTP_201_CREATED,
    )
    create_payment.assert_called_once()

    get_payment_detail = mocker.patch(
        "src.controllers.payment_controller.PaymentService.get_payment_detail",
        return_value=payment,
    )
    assert_success(PaymentDetailAPIView().get(make_request(payment.owner), payment.id))
    get_payment_detail.assert_called_once_with(payment.owner, payment.id)

    confirm_payment = mocker.patch(
        "src.controllers.payment_controller.PaymentService.confirm_payment",
        return_value=payment,
    )
    assert_success(PaymentConfirmAPIView().post(make_request(payment.owner), payment.id))
    confirm_payment.assert_called_once_with(payment.owner, payment.id)
