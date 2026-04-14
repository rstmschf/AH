from django.contrib import admin
from .models import Bid


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "bidder", "bid_amount", "item", "created_at")
    list_filter = ("created_at",)
    list_select_related = ("bidder", "item")
    ordering = ("-created_at",)
    search_fields = ("bidder__username", "item__name")
    autocomplete_fields = ("bidder", "item")

