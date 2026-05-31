from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Wishlist, WishlistItem
from .serializers import WishlistSerializer, WishlistItemSerializer
from product.models import Product
from django.shortcuts import get_object_or_404

class WishlistRetrieveView(generics.RetrieveAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist

class WishlistAddRemoveView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WishlistItemSerializer

    def post(self, request):
        product_id = request.data.get("product")
        product = get_object_or_404(Product, pk=product_id)
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
        if created:
            return Response({"detail": "Added to wishlist"}, status=201)
        return Response({"detail": "Already in wishlist"}, status=200)

    def delete(self, request):
        product_id = request.data.get("product")
        product = get_object_or_404(Product, pk=product_id)
        wishlist = get_object_or_404(Wishlist, user=request.user)
        item = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
        if item:
            item.delete()
            return Response({"detail": "Removed from wishlist"}, status=204)
        return Response({"error": "Item not in wishlist"}, status=404)