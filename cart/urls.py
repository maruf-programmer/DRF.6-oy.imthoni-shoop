from django.urls import path
from .views import (
    CartRetrieveUpdateView,
    AddToCartView,
    UpdateCartItemView,
    RemoveFromCartView,
)

urlpatterns = [
    path("", CartRetrieveUpdateView.as_view(), name="cart-detail"),
    path("items/", AddToCartView.as_view(), name="cart-add-item"),
    path("items/<uuid:pk>/", UpdateCartItemView.as_view(), name="cart-update-item"),
    path("items/<uuid:pk>/delete/", RemoveFromCartView.as_view(), name="cart-remove-item"),
]