from rest_framework import serializers
from .models import Wishlist, WishlistItem

class WishlistItemSerializer(serializers.ModelSerializer):
    product_title = serializers.ReadOnlyField(source="product.title")

    class Meta:
        model = WishlistItem
        fields = ["id", "product", "product_title"]

class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "items"]