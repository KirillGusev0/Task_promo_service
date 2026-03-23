from django.contrib import admin
from orders.models import Product, Category, PromoCode, Order

# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "price",
        "category",
        "is_excluded_from_promos",
    )

    list_display_links = ("id", "name")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
    )

    list_display_links = ("id", "name")


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "code",
        "discount_percent",
        "max_uses",
        "used_count",
        "active_from",
        "active_to",
    )

    list_display_links = ("id", "code")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "price",
        "discount",
        "total",
        "created_at",
    )

    list_display_links = ("id",)
