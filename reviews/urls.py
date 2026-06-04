from django.urls import path
from .views import ReviewApproveView, ReviewDetailView, ReviewListCreateView

urlpatterns = [
    path("", ReviewListCreateView.as_view(), name="review-list"),
    path("<uuid:pk>/", ReviewDetailView.as_view(), name="review-detail"),
    path("<uuid:pk>/approve/", ReviewApproveView.as_view(), name="review-approve"),
]
