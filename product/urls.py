from django.urls import path
from .views import (
    ProductDetailView,
    ProductImageDeleteView,
    ProductImageUploadView,
    ProductListCreateView,
    ProductMainImageView,
)

urlpatterns = [
    path("", ProductListCreateView.as_view(), name="product-list"),
    path("<uuid:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("<uuid:pk>/upload-image/", ProductImageUploadView.as_view(), name="product-upload-image"),
    path(
        "<uuid:pk>/set-main-image/<uuid:image_pk>/",
        ProductMainImageView.as_view(),
        name="product-set-main-image",
    ),
    path(
        "<uuid:pk>/delete-image/<uuid:image_pk>/",
        ProductImageDeleteView.as_view(),
        name="product-delete-image",
    ),
]
