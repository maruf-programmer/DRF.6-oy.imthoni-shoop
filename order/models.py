from django.db import models
from shared.models import BaseModel


class Status(models.TextChoices):
    PENDING = "pending"
    PAID = "paid"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(BaseModel):
    user = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.CASCADE, related_name="orders"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=2)


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
