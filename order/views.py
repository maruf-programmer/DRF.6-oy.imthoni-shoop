from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart
from payments.models import Payment
from shared.permissions import IsOrderOwnerOrAdmin
from .models import Order, OrderItem
from .serializers import OrderSerializer


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_role == "admin":
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.user_role == "admin":
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user, total_price=0)
        total_price = 0

        for cart_item in cart.items.all():
            product = cart_item.product

            if product.stock < cart_item.quantity:
                order.delete()
                return Response(
                    {"error": f"Not enough stock for {product.title}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            price = product.discount_price or product.price
            item_total = price * cart_item.quantity

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart_item.quantity,
                total_price=item_total,
            )

            product.stock -= cart_item.quantity
            product.save()
            total_price += item_total

        order.total_price = total_price
        order.save()
        Payment.objects.create(
            order=order,
            amount=total_price,
            payment_method="cash",
        )
        cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated, IsOrderOwnerOrAdmin]
    serializer_class = OrderSerializer

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        self.check_object_permissions(request, order)

        if order.status != "pending":
            return Response(
                {"error": "Only pending orders can be cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save()

        order.status = "cancelled"
        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data)
