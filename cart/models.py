from django.db import models
from shared.models import BaseModel


class Cart(BaseModel):
    user = models.OneToOneField(
        "accounts.CustomUser",
        on_delete=models.CASCADE
    )

class CartItem(BaseModel):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        "product.Product",
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
