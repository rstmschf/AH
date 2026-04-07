from django.db import models
from django.conf import settings
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE


class Item(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    auction = models.ForeignKey(
        "auctions.Auction", on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=700, blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    current_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    won_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="won_items",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.auction.name})"

    @property
    def is_won(self):
        return self.won_by_id is not None
