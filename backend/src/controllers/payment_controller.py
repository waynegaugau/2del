from rest_framework import status
from rest_framework.views import APIView

from src.common.permissions import IsPetOwnerRole
from src.common.responses import success_response
from src.serializers.payment_serializer import (
    PaymentCreateSerializer,
    PaymentSerializer,
)
from src.services.payment_service import PaymentService


class PaymentListCreateAPIView(APIView):
    permission_classes = [IsPetOwnerRole]

    def get(self, request):
        payments = PaymentService.get_user_payments(request.user)
        serializer = PaymentSerializer(payments, many=True)
        return success_response(serializer.data, "Lấy danh sách thanh toán thành công")

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = PaymentService.create_payment(request.user, serializer.validated_data)
        output = PaymentSerializer(payment)
        return success_response(
            output.data,
            "Tạo thanh toán thành công",
            status.HTTP_201_CREATED,
        )


class PaymentDetailAPIView(APIView):
    permission_classes = [IsPetOwnerRole]

    def get(self, request, payment_id):
        payment = PaymentService.get_payment_detail(request.user, payment_id)
        serializer = PaymentSerializer(payment)
        return success_response(serializer.data, "Lấy chi tiết thanh toán thành công")


class PaymentConfirmAPIView(APIView):
    permission_classes = [IsPetOwnerRole]

    def post(self, request, payment_id):
        payment = PaymentService.confirm_payment(request.user, payment_id)
        serializer = PaymentSerializer(payment)
        return success_response(serializer.data, "Xác nhận thanh toán thành công")
