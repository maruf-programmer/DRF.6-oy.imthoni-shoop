from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from shared.permissions import IsOwnerOrAdmin
from .models import Review
from .serializers import ReviewSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(description="Tasdiqlangan sharhlar ro'yxati (o'zinikini ham ko'radi)."),
    create=extend_schema(description="Yangi sharh qoldirish."),
    retrieve=extend_schema(description="Bitta sharh."),
    update=extend_schema(description="Sharhni yangilash (egasi yoki admin)."),
    partial_update=extend_schema(description="Sharhni qisman yangilash."),
    destroy=extend_schema(description="Sharhni o'chirish (egasi yoki admin)."),
)
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
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

    @extend_schema(description="Sharhni admin tomonidan tasdiqlash.")
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        review = self.get_object()
        if not request.user.user_role == "admin":
            return Response({"error": "Only admin can approve"}, status=403)
        review.is_approved = True
        review.save()
        return Response(ReviewSerializer(review).data)