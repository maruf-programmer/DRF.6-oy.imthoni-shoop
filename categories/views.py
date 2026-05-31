from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from shared.permissions import IsAdminOrReadOnly
from .models import Category
from .serializers import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"   # or "pk" – choose one; I'd use pk for consistency with UUID