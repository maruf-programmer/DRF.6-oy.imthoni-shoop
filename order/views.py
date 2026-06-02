from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from shared.permissions import IsOrderOwnerOrAdmin
from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(description="Foydalanuvchining barcha buyurtmalari (admin hammasini ko'radi)."),
    retrieve=extend_schema(description="Bitta buyurtma tafsilotlari."),
    partial_update=extend_schema(description="Buyurtma holatini yangilash (admin)."),
)
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_role == "admin":
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def get_permissions(self):
        if self.action in ["retrieve", "update", "partial_update", "destroy", "cancel"]:
            self.permission_classes = [IsAuthenticated, IsOrderOwnerOrAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @extend_schema(
        description="Savatdagi barcha mahsulotlarni buyurtmaga o'tkazish. Savat tozalanadi.",
        responses={201: OrderSerializer},
    )
    @action(detail=False, methods=["post"])
    def checkout(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        total = 0
        order = Order.objects.create(user=request.user, total_price=0)
        for item in cart.items.all():
            if item.product.stock < item.quantity:
                order.delete()
                return Response({"error": f"Not enough stock for {item.product.title}"}, status=400)
            price = item.product.discount_price or item.product.price
            item_total = price * item.quantity
            OrderItem.objects.create(
                order=order, product=item.product, quantity=item.quantity, total_price=item_total
            )
            total += item_total
            item.product.stock -= item.quantity
            item.product.save()

        order.total_price = total
        order.save()
        cart.items.all().delete()
        return Response(OrderSerializer(order).data, status=201)

    @extend_schema(description="Buyurtmani bekor qilish (faqat 'pending' holatda).")
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status != "pending":
            return Response({"error": "Only pending orders can be cancelled"}, status=400)
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save()
        order.status = "cancelled"
        order.save()
        return Response(OrderSerializer(order).data)