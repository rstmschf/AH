from rest_framework import serializers
from .models import Auction
from items.serializers import ItemListSerializer


class AuctionDateValidationMixin:
    def validate(self, data):
        date_start = data.get("date_start") or getattr(
            self.instance, "date_start", None
        )
        date_end = data.get("date_end") or getattr(self.instance, "date_end", None)
        if date_end and date_start and date_end <= date_start:
            raise serializers.ValidationError(
                {"date_end": "End date must be after start date."}
            )
        return data


class AuctionCreateSerializer(AuctionDateValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = (
            "id",
            "name",
            "description",
            "currency",
            "date_start",
            "date_end",
            "is_public"
        )


class AuctionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = (
            "id",
            "status",
            "name",
            "currency",
            "date_start",
            "date_end",
        )


class AuctionDetailSerializer(AuctionDateValidationMixin, serializers.ModelSerializer):
    items = ItemListSerializer(many=True, read_only=True)
    auctioneer = serializers.CharField(source="auctioneer.username", read_only=True)

    class Meta:
        model = Auction
        fields = (
            "id",
            "status",
            "name",
            "description",
            "currency",
            "auctioneer",
            "created_at",
            "date_start",
            "date_end",
            "updated_at",
            "items",
        )
        read_only_fields = (
            "id",
            "items",
            "status",
            "auctioneer",
            "created_at",
            "updated_at",
        )


class AuctionOwnerSerializer(AuctionDetailSerializer):
    class Meta(AuctionDetailSerializer.Meta):
        fields = AuctionDetailSerializer.Meta.fields + ("invite_code", "is_public")
        read_only_fields = AuctionDetailSerializer.Meta.read_only_fields + (
            "invite_code",
        )
