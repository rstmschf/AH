from rest_framework import viewsets, permissions
from .models import Auction, AuctionParticipant
from .serializers import (
    AuctionCreateSerializer,
    AuctionDetailSerializer,
    AuctionOwnerSerializer,
    AuctionListSerializer,
)
from .permissions import IsAuctioneerOrReadOnly
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response


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

    @action(detail=False, methods=["post"], url_path="join/(?P<invite_code>[^/.]+)")
    def join(self, request, invite_code=None):
        auction = get_object_or_404(Auction, invite_code=invite_code)
        AuctionParticipant.objects.get_or_create(
            auction=auction, participant=request.user
        )
        return Response({"joined": auction.name}, status=200)
    
    @action(detail=True, methods=["post"])
    def leave(self, request, pk=None):
        auction = self.get_object()
        deleted, _ = AuctionParticipant.objects.filter(
            auction=auction, participant=request.user
        ).delete()
        if not deleted:
            return Response({"detail": "You are not a participant."}, status=400)
        return Response({"detail": "Left auction."}, status=200)