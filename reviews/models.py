from django.db import models

from shared.models import BaseModel


class Review(BaseModel):
    user = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.CASCADE, related_name="reviews"
    )
    product = models.ForeignKey(
        "product.Product", on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_user_product_review"
            ),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"
