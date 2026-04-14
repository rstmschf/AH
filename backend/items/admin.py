from django.contrib import admin
from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "base_price", "current_price", "auction", "won_by", "created_at", "bid_step")
    readonly_fields = ("current_price",)
    list_filter = ("created_at", "auction__status")
    list_select_related = ("auction", "won_by")
    ordering = ("-created_at",)
    search_fields = ("name", "auction__name",)
    autocomplete_fields = ("auction", "won_by")


