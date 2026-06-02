from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'is_main']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'category', 'seller', 'price', 'discount_price', 'stock', 'status', 'created_at']
    list_filter = ['status', 'category', 'seller']
    search_fields = ['title', 'description', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'is_main']
    list_filter = ['is_main']
    search_fields = ['product__title']