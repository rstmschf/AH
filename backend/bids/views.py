from django.db import transaction
from rest_framework import viewsets, permissions
from .serializers import BidCreateSerializer, BidListAndDetailSerializer
from .models import Bid
from items.models import Item
from rest_framework.exceptions import ValidationError
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

    @transaction.atomic
    def perform_create(self, serializer):
        item = Item.objects.select_for_update().select_related("auction").get(
            pk=self.kwargs["item_pk"]
        )
        min_price = (item.current_price or item.base_price) + item.bid_step
        if serializer.validated_data["bid_amount"] < min_price:
            raise ValidationError(
                {"bid_amount": f"Minimal bid is now {min_price}."}
            )
        bid = serializer.save(bidder=self.request.user, item=item)
        item.current_price = bid.bid_amount
        item.save(update_fields=["current_price"])
    