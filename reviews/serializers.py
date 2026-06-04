from rest_framework import serializers
from .models import Review
from django.core.validators import MinValueValidator, MaxValueValidator


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Review
        fields = ["id", "user", "user_name", "product", "rating", "title", "comment", "is_approved", "created_at"]
        read_only_fields = ["id", "user", "is_approved", "created_at"]
        extra_kwargs = {
            "rating": {"validators": [MinValueValidator(1), MaxValueValidator(5)]}
        }

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
