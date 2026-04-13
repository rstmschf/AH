from django.db import models
from django.conf import settings
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE
from decimal import Decimal


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
        related_name="items_won",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bid_step = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("1.00"))

    def __str__(self):
        return f"{self.name} ({self.auction.name})"

    @property
    def is_won(self):
        return self.won_by_id is not None


class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="items/%Y/%m/")
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_primary:
            ItemImage.objects.filter(item=self.item, is_primary=True).exclude(
                pk=self.pk
            ).update(is_primary=False)
        super().save(*args, **kwargs)
