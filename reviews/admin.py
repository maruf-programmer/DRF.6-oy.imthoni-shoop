from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating']
    search_fields = ['user__username', 'product__title', 'comment']
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} ta sharh tasdiqlandi.")
    approve_reviews.short_description = "Tanlangan sharhlarni tasdiqlash"