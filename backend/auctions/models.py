from django.db import models
from django.conf import settings
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE
from .services import generate_invite_code


class Auction(SafeDeleteModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed"
        CANCELED = "canceled", "Canceled"

    _safedelete_policy = SOFT_DELETE_CASCADE
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    name = models.CharField(max_length=255)
    description = models.TextField(
        blank=True,
        max_length=700,
        verbose_name="Auction Description",
        help_text="Describe auction's items, reasons, goals.",
    )
    auctioneer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="auctions_created",
    )
    invite_code = models.CharField(
        max_length=32, unique=True, db_index=True, default=generate_invite_code
    )
    created_at = models.DateTimeField(auto_now_add=True)
    date_start = models.DateTimeField(blank=False)
    date_end = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Auctions"
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["name"]), models.Index(fields=["auctioneer"])]

    def __str__(self):
        return self.name
