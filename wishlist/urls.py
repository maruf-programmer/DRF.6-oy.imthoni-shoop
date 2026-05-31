from django.urls import path
from .views import WishlistRetrieveView, WishlistAddRemoveView

urlpatterns = [
    path("", WishlistRetrieveView.as_view(), name="wishlist-detail"),
    path("items/", WishlistAddRemoveView.as_view(), name="wishlist-add-remove"),
]