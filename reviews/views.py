from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.permissions import IsOwnerOrAdmin
from .models import Review
from .serializers import ReviewSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_role == "admin":
            return Review.objects.all()

        approved_reviews = Review.objects.filter(is_approved=True)
        my_reviews = Review.objects.filter(user=self.request.user)
        return (approved_reviews | my_reviews).distinct()


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        if self.request.user.user_role == "admin":
            return Review.objects.all()

        approved_reviews = Review.objects.filter(is_approved=True)
        my_reviews = Review.objects.filter(user=self.request.user)
        return (approved_reviews | my_reviews).distinct()

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return [IsAuthenticated()]


class ReviewApproveView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    def post(self, request, pk):
        if request.user.user_role != "admin":
            return Response(
                {"error": "Only admin can approve"},
                status=status.HTTP_403_FORBIDDEN,
            )

        review = get_object_or_404(Review, pk=pk)
        review.is_approved = True
        review.save()

        serializer = ReviewSerializer(review)
        return Response(serializer.data)
