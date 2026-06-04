from django.urls import path
from .views import CategoryDetailView, CategoryListCreateView

urlpatterns = [
    path("", CategoryListCreateView.as_view(), name="category-list"),
    path("<slug:slug>/", CategoryDetailView.as_view(), name="category-detail"),
]
