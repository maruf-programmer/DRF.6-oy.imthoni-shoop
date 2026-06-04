from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.permissions import IsSellerOrAdmin, IsSellerOwnerOrAdmin
from .models import Product, ProductImage
from .serializers import ProductImageSerializer, ProductSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.user_role == "admin":
            return Product.objects.all()
        return Product.objects.filter(status="published")

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsSellerOrAdmin()]
        return []

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsSellerOwnerOrAdmin()]
        return []


class ProductImageUploadView(APIView):
    permission_classes = [IsAuthenticated, IsSellerOwnerOrAdmin]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ProductImageSerializer

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        self.check_object_permissions(request, product)

        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductMainImageView(APIView):
    permission_classes = [IsAuthenticated, IsSellerOwnerOrAdmin]
    serializer_class = ProductImageSerializer

    def post(self, request, pk, image_pk):
        product = get_object_or_404(Product, pk=pk)
        self.check_object_permissions(request, product)

        image = product.images.filter(pk=image_pk).first()
        if not image:
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        product.images.update(is_main=False)
        image.is_main = True
        image.save()
        return Response({"status": "main image set"})


class ProductImageDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsSellerOwnerOrAdmin]
    serializer_class = ProductImageSerializer

    def delete(self, request, pk, image_pk):
        product = get_object_or_404(Product, pk=pk)
        self.check_object_permissions(request, product)

        image = product.images.filter(pk=image_pk).first()
        if not image:
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
