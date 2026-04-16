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
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from django.db.models import Q


class AuctionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAuctioneerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return (
            Auction.objects
            .select_related("auctioneer")
            .prefetch_related("items", "participants")
            .filter(Q(is_public=True) | Q(auctioneer=user) | Q(participants=user))
            .distinct()
        )

    def get_serializer_class(self):
        if self.action == "list":
            return AuctionListSerializer
        if self.action == "create":
            return AuctionCreateSerializer
        if self.action in ("update", "partial_update"):
            return AuctionOwnerSerializer
        return AuctionDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        ctx = self.get_serializer_context()
        if instance.auctioneer_id == request.user.id:
            serializer_class = AuctionOwnerSerializer
        else:
            serializer_class = AuctionDetailSerializer
        serializer = serializer_class(instance, context=ctx)
        return Response(serializer.data)
    
        
    def perform_create(self, serializer):
        serializer.save(auctioneer=self.request.user)

    def get_permissions(self):
        if self.action in ("join", "leave"):
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=["post"], url_path="join/(?P<invite_code>[^/.]+)")
    def join(self, request, invite_code=None, **kwargs):
        auction = get_object_or_404(Auction, invite_code=invite_code)
        AuctionParticipant.objects.get_or_create(
            auction=auction, participant=request.user
        )
        return Response({"joined": auction.name}, status=HTTP_200_OK)
    
    @action(detail=True, methods=["post"])
    def leave(self, request, pk=None, **kwargs):
        auction = self.get_object()
        deleted, _ = AuctionParticipant.objects.filter(
            auction=auction, participant=request.user
        ).delete()
        if not deleted:
            return Response({"detail": "You are not a participant."}, status=HTTP_404_NOT_FOUND)
        return Response({"detail": "Left auction."}, status=HTTP_200_OK)
    
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None, **kwargs):
        auction = self.get_object()
        if auction.status not in (Auction.Status.PENDING, Auction.Status.ACTIVE):
            return Response(
                {"detail": f"Cannot cancel auction in status '{auction.status}'."},
                status=HTTP_400_BAD_REQUEST,
            )
        auction.status = Auction.Status.CANCELED
        auction.save(update_fields=["status"])
        return Response({"detail": "Auction canceled."}, status=HTTP_200_OK)
        
            