from django.db import models
from django.conf import settings
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE


class Bid(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    bidder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="bids",
    )
    bid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(
        "items.Item", on_delete=models.SET_NULL, null=True, related_name="bids"
    )

    def __str__(self):
        return f"{self.bid_amount} on {self.item_id} by {self.bidder_id}"

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["item","-created_at"])]