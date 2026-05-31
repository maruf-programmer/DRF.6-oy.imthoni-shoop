from django.db import models
from shared.models import BaseModel

class Category(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    image = models.ImageField(upload_to="categories/")

    def __str__(self):
        return self.name
