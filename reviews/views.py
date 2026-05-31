from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from shared.permissions import IsOwnerOrAdmin
from .models import Review
from .serializers import ReviewSerializer
from rest_framework.decorators import action

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]  # must be logged in to write reviews

    def get_queryset(self):
        # Public can see approved reviews; admin sees all; user sees own + approved
        if self.request.user.is_authenticated and self.request.user.user_role == "admin":
            return Review.objects.all()
        base = Review.objects.filter(is_approved=True)
        if self.request.user.is_authenticated:
            base = base | Review.objects.filter(user=self.request.user)
        return base.distinct()

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        review = self.get_object()
        if not request.user.user_role == "admin":
            return Response({"error": "Only admin can approve"}, status=403)
        review.is_approved = True
        review.save()
        return Response(ReviewSerializer(review).data)