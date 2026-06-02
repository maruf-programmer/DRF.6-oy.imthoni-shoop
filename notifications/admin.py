from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message_preview', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['user__username', 'message']
    actions = ['mark_as_read']

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Xabar'

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} ta bildirishnoma o'qildi.")
    mark_as_read.short_description = "Tanlangan bildirishnomalarni o‘qilgan deb belgilash"