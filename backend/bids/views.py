from rest_framework import viewsets, permissions
from .serializers import BidCreateSerializer, BidListAndDetailSerializer
from .models import Bid
from items.models import Item
from django.shortcuts import get_object_or_404

class BidViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bid.objects.select_related("item", "bidder").filter(
            item_id=self.kwargs["item_pk"]
        )
    
    def get_serializer_class(self):
        if self.action == "create":
            return BidCreateSerializer
        return BidListAndDetailSerializer
    
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if self.action == "create":
            ctx["item"] = get_object_or_404(
                Item.objects.select_related("auction"),
                pk=self.kwargs["item_pk"],
            )
        return ctx

    def perform_create(self, serializer):
        item = serializer.context["item"]
        bid = serializer.save(bidder=self.request.user, item=item)
        item.current_price = bid.bid_amount
        item.save(update_fields=["current_price"])