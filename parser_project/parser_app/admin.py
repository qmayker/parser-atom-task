from django.contrib import admin

from .models import Product

# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "color",
        "storage",
        "product_code",
        "reviews",
        "created_at",
    )
    list_filter = ("created_at", "updated_at", "color", "storage")
    search_fields = ("title", "product_code")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Основна інформація", {"fields": ("title", "url", "product_code")}),
        (
            "Характеристики",
            {"fields": ("color", "storage", "screen_diagonal", "display_resolution")},
        ),
        ("Медіа", {"fields": ("photos",)}),
        (
            "Додатково",
            {"fields": ("reviews", "characteristics", "created_at", "updated_at")},
        ),
    )
