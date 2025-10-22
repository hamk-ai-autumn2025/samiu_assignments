from django.contrib import admin
from .models import Product, Service

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price_eur", "in_stock", "created_at")
    list_filter = ("category", "in_stock")
    search_fields = ("name",)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "active")
    list_filter = ("active",)
    search_fields = ("title", "description")
