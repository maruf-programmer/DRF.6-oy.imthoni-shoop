from rest_framework import serializers
from .models import Cart, CartItem
from product.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.ReadOnlyField(source="product.title")
    product_price = serializers.ReadOnlyField(source="product.price")

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_title", "product_price", "quantity"]
        read_only_fields = ["id"]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]

    def get_total_price(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())