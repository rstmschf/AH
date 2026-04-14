from rest_framework import viewsets, permissions
from .models import Item, ItemImage
from .serializers import (
    ItemCreateSerializer,
    ItemDetailSerializer,
    ItemListSerializer,
    ImageCreateSerializer,
    ImageShowSerializer,
    ImageUpdateSerializer,
)
from auctions.permissions import IsAuctioneerOrReadOnly
from auctions.models import Auction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.select_related("auction", "won_by").prefetch_related(
        "images"
    )
    permission_classes = [permissions.IsAuthenticated, IsAuctioneerOrReadOnly]

    def get_queryset(self):
        return super().get_queryset().filter(auction_id=self.kwargs["auction_pk"])

    def get_serializer_class(self):
        if self.action == "list":
            return ItemListSerializer
        if self.action == "create":
            return ItemCreateSerializer
        return ItemDetailSerializer

    def perform_create(self, serializer):
        auction = get_object_or_404(Auction, pk=self.kwargs["auction_pk"])
        if auction.auctioneer_id != self.request.user.id:
            raise PermissionDenied("You are not the auctioneer of this auction.")
        serializer.save(auction=auction)


class ItemImageViewSet(viewsets.ModelViewSet):
    queryset = ItemImage.objects.select_related("item__auction")
    permission_classes = [permissions.IsAuthenticated, IsAuctioneerOrReadOnly]

    def get_queryset(self):
        return super().get_queryset().filter(item_id=self.kwargs["item_pk"])

    def get_serializer_class(self):
        if self.action == "create":
            return ImageCreateSerializer
        if self.action in ("update", "partial_update"):
            return ImageUpdateSerializer
        return ImageShowSerializer

    def perform_create(self, serializer):
        item = get_object_or_404(Item, pk=self.kwargs["item_pk"])
        if item.auction.auctioneer_id != self.request.user.id:
            raise PermissionDenied("You are not the auctioneer of this auction.")
        serializer.save(item=item)
