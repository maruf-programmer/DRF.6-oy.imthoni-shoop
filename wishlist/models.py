from django.db import models

from shared.models import BaseModel


class Wishlist(BaseModel):
    user = models.OneToOneField(
        "accounts.CustomUser", on_delete=models.CASCADE, related_name="wishlist"
    )

    def __str__(self):
        return f"{self.user.username} wishlist"


class WishlistItem(BaseModel):
    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        "product.Product", on_delete=models.CASCADE, related_name="wishlist_items"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["wishlist", "product"], name="unique_wishlist_product"
            ),
        ]

    def __str__(self):
        return f"{self.wishlist.user.username} - {self.product.title}"
