from django.db import models
from categories.models import Category
from shared.models import BaseModel


class Status(models.TextChoices):
    DRAFT = "draft", "Qoralama"
    PUBLISHED = "published", "E'lon berilgan"


class Product(BaseModel):
    seller = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="products",
        blank=True,
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    stock = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )

    def __str__(self):
        return self.title


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.title} image"
