from rest_framework import viewsets, permissions
from .models import Auction
from .serializers import (
    AuctionCreateSerializer,
    AuctionDetailSerializer,
    AuctionOwnerSerializer,
    AuctionListSerializer,
)
from .permissions import IsAuctioneerOrReadOnly

class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.select_related("auctioneer").prefetch_related("items")
    permission_classes = [permissions.IsAuthenticated, IsAuctioneerOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return AuctionListSerializer
        if self.action == "create":
            return AuctionCreateSerializer
        if self.action in ("update", "partial_update"):
            return AuctionOwnerSerializer
        if self.action == "retrieve":
            obj = self.get_object()
            if obj.auctioneer_id == self.request.user.id:
                return AuctionOwnerSerializer
            return AuctionDetailSerializer
        return AuctionDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(auctioneer=self.request.user)