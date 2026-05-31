from django.db import models
from django.conf import settings
from shared.models import BaseModel

class PaymentStatus(models.TextChoices):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Payment(BaseModel):
    order = models.OneToOneField(
        "order.Order",
        on_delete=models.CASCADE,
        related_name="payment"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    payment_method = models.CharField(max_length=50, blank=True)  # e.g., payme, stripe
    transaction_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id} - {self.status}"