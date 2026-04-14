from rest_framework import serializers
from .models import Bid
from auctions.models import AuctionParticipant


class BidListAndDetailSerializer(serializers.ModelSerializer):
    bidder = serializers.CharField(source="bidder.username", read_only=True)
    class Meta:
        model = Bid
        fields = ("id", "bidder", "bid_amount", "created_at")


class BidCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ("id", "bid_amount")

    def validate_bid_amount(self, value):
        item = self.context["item"]
        min_price = (item.current_price or item.base_price) + item.bid_step
        if value < min_price:
            raise serializers.ValidationError(
                f"Minimal bid possible is {min_price}."
            )
        return value
    
    def validate(self, data):
        item = self.context["item"]
        request = self.context.get("request")
        if request and item.auction.auctioneer_id == request.user.id:
            raise serializers.ValidationError("Cannot bid on your own auction.")
        if item.auction.status != "active":
            raise serializers.ValidationError("Auction is not active.")
        if request and not AuctionParticipant.objects.filter(
            auction_id=item.auction_id, participant_id=request.user.id
        ).exists():
            raise serializers.ValidationError("You are not a participant of this auction.")
        return data