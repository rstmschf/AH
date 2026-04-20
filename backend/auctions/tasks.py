from celery import shared_task
from django.db import transaction
from django.utils import timezone
from .models import Auction

@shared_task
def close_expired_auctions():
    now = timezone.now()
    expired = Auction.objects.filter(
        status="active", date_end__isnull=False, date_end__lte=now
    )
    for auction in expired:
        close_auction.delay(auction.id)

@shared_task
def close_auction(auction_id):
    with transaction.atomic():
        auction = Auction.objects.select_for_update().get(pk=auction_id)
        if auction.status != "active":
            return
        for item in auction.items.all():
            top = item.bids.order_by("-bid_amount", "created_at").first()
            if top:
                item.won_by_id = top.bidder_id
                item.save(update_fields=["won_by"])
        auction.status = "closed"
        auction.save(update_fields=["status"])