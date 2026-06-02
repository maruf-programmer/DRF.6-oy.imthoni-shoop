from rest_framework import serializers
from .models import Product, ProductImage
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "is_main"]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Yangi mahsulot misoli",
            value={
                "category": "uuid-of-category",
                "title": "iPhone 15",
                "description": "Ajoyib smartfon",
                "price": "999.99",
                "stock": 10,
            },
            request_only=True,
        ),
    ]
)
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
        validated_data["seller"] = self.context["request"].user
        from django.utils.text import slugify
        validated_data["slug"] = slugify(validated_data["title"])
        return super().create(validated_data)