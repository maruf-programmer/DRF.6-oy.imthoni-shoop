from rest_framework import serializers
from .models import Product, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "is_main"]
        read_only_fields = ["id"]

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    seller_name = serializers.ReadOnlyField(source="seller.username")

    class Meta:
        model = Product
        fields = [
            "id", "seller", "seller_name", "category", "title", "slug",
            "description", "price", "discount_price", "stock", "status",
            "images", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "seller", "slug", "created_at", "updated_at"]

    def create(self, validated_data):
        # Auto-set seller to the authenticated user
        validated_data["seller"] = self.context["request"].user
        # Auto-generate slug from title (simple version)
        from django.utils.text import slugify
        validated_data["slug"] = slugify(validated_data["title"])
        return super().create(validated_data)