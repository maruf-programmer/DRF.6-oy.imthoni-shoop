from django.urls import path
from .views import CheckoutView, OrderCancelView, OrderDetailView, OrderListView

urlpatterns = [
    path("", OrderListView.as_view(), name="order-list"),
    path("checkout/", CheckoutView.as_view(), name="order-checkout"),
    path("<uuid:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("<uuid:pk>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
]
