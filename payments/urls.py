from django.urls import path
from .views import PaymentConfirmView, PaymentDetailView, PaymentListView

urlpatterns = [
    path("", PaymentListView.as_view(), name="payment-list"),
    path("<uuid:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
    path("<uuid:pk>/confirm/", PaymentConfirmView.as_view(), name="payment-confirm"),
]
