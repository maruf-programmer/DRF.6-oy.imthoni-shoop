from rest_framework import serializers
from .models import Cart, CartItem
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample


class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.ReadOnlyField(source="product.title")
    product_price = serializers.ReadOnlyField(source="product.price")

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_title", "product_price", "quantity"]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Savatga qo'shish misoli",
            value={"product": "uuid", "quantity": 2},
            request_only=True,
        ),
    ]
)
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]

    def get_total_price(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())