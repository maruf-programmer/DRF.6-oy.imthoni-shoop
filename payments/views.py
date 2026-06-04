from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from .serializers import PaymentSerializer


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_role == "admin":
            return Payment.objects.all()
        return Payment.objects.filter(order__user=self.request.user)


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_role == "admin":
            return Payment.objects.all()
        return Payment.objects.filter(order__user=self.request.user)


class PaymentConfirmView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def post(self, request, pk):
        payment = get_object_or_404(self.get_queryset(), pk=pk)

        if payment.status != "pending":
            return Response(
                {"error": "Payment already processed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.status = "completed"
        payment.transaction_id = "simulated_txn_id"
        payment.save()

        payment.order.status = "paid"
        payment.order.save()

        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

    def get_queryset(self):
        if self.request.user.user_role == "admin":
            return Payment.objects.all()
        return Payment.objects.filter(order__user=self.request.user)
