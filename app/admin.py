from django.contrib import admin
from .models import Restaurant, Food, Order, DeliveryPartner


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("id", "rest_name", "location")
    search_fields = ("rest_name", "location")


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "restaurant", "price", "available")
    list_filter = ("available", "restaurant")
    search_fields = ("name", "restaurant__rest_name")
    list_editable = ("price", "available")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "food",
        "quantity",
        "total_price",
        "status",
        "ordered_at",
    )
    list_filter = ("status", "ordered_at")
    search_fields = ("customer__username", "food__name", "phone")
    list_editable = ("status",)
    readonly_fields = ("ordered_at",)


@admin.register(DeliveryPartner)
class DeliveryPartnerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "available")
    list_filter = ("available",)
    search_fields = ("name", "phone")
    list_editable = ("available",)