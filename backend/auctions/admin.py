from django.contrib import admin
from .models import Auction, AuctionParticipant


class AuctionParticipantInline(admin.TabularInline):
    model = AuctionParticipant
    extra = 1
    autocomplete_fields = ("participant",)


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    inlines = [AuctionParticipantInline]
    list_display = ("id", "name", "status", "auctioneer", "is_public", "created_at")
    list_filter = ("created_at", "is_public", "status")
    list_select_related = ("auctioneer",)
    ordering = ("-created_at",)
    search_fields = ("name", "auctioneer__username", "auctioneer__email")
    autocomplete_fields = ("auctioneer",)
