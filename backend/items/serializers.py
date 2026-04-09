from rest_framework import serializers
from .models import Item, ItemImage


class ImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        fields = ("image", "is_primary")


class ImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        fields = ("id", "image", "is_primary")


class ImageShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        fields = ("id", "image", "is_primary")
        read_only_fields = ("id", "image", "is_primary")


class ItemListSerializer(serializers.ModelSerializer):
    images = ImageShowSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = ("id", "name", "current_price", "images")


class ItemDetailSerializer(serializers.ModelSerializer):
    images = ImageShowSerializer(many=True, read_only=True)
    auction = serializers.CharField(source="auction.name", read_only=True)

    class Meta:
        model = Item
        fields = (
            "id",
            "auction",
            "name",
            "base_price",
            "current_price",
            "description",
            "images",
            "created_at",
            "won_by",
        )
        read_only_fields = (
            "id",
            "won_by",
            "created_at",
            "current_price",
            "auction"
        )


class ItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ("id", "name", "base_price", "description")
