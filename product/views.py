from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from shared.permissions import IsSellerOrAdmin, IsSellerOwnerOrAdmin
from .models import Product, ProductImage
from .serializers import ProductSerializer, ProductImageSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(description="Barcha e'lon qilingan mahsulotlarni ko'rish (admin uchun hammasi)."),
    create=extend_schema(description="Yangi mahsulot qo'shish (sotuvchi yoki admin)."),
    retrieve=extend_schema(description="Bitta mahsulotni ko'rish."),
    update=extend_schema(description="Mahsulotni to'liq yangilash (egasi yoki admin)."),
    partial_update=extend_schema(description="Mahsulotni qisman yangilash."),
    destroy=extend_schema(description="Mahsulotni o'chirish (egasi yoki admin)."),
)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsSellerOrAdmin]
        elif self.action in ["upload_image", "delete_image", "set_main_image"]:
            self.permission_classes = [IsAuthenticated, IsSellerOwnerOrAdmin]
        else:
            self.permission_classes = []
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated and self.request.user.user_role == "admin":
            return qs
        if self.action == "list":
            return qs.filter(status="published")
        return qs

    @extend_schema(
        description="Mahsulotga yangi rasm yuklash (multipart/form-data).",
        request=ProductImageSerializer,
    )
    @action(detail=True, methods=["post"], url_path="upload-image")
    def upload_image(self, request, pk=None):
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @extend_schema(
        description="Berilgan rasmni asosiy rasm qilish.",
    )
    @action(detail=True, methods=["post"], url_path="set-main-image/(?P<image_pk>[^/.]+)")
    def set_main_image(self, request, pk=None, image_pk=None):
        product = self.get_object()
        try:
            image = product.images.get(pk=image_pk)
            product.images.update(is_main=False)
            image.is_main = True
            image.save()
            return Response({"status": "main image set"})
        except ProductImage.DoesNotExist:
            return Response({"error": "Image not found"}, status=404)

    @extend_schema(
        description="Mahsulotdan rasmni o'chirish.",
    )
    @action(detail=True, methods=["delete"], url_path="delete-image/(?P<image_pk>[^/.]+)")
    def delete_image(self, request, pk=None, image_pk=None):
        product = self.get_object()
        try:
            image = product.images.get(pk=image_pk)
            image.delete()
            return Response(status=204)
        except ProductImage.DoesNotExist:
            return Response(status=404)