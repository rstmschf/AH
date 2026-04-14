import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from auctions.models import Auction, AuctionParticipant
from items.models import Item
from bids.models import Bid

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"testuser{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@mail.com")
    password = factory.PostGenerationMethodCall("set_password", "testpassword")


class AuctionFactory(DjangoModelFactory):
    class Meta:
        model = Auction

    name = factory.Sequence(lambda n: f"Auction {n}")
    description = "Test auction"
    currency = "USD"
    auctioneer = factory.SubFactory(UserFactory)
    is_public = False
    status = "active"
    date_start = factory.LazyFunction(lambda: timezone.now() - timedelta(days=1))
    date_end = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))


class AuctionParticipantFactory(DjangoModelFactory):
    class Meta:
        model = AuctionParticipant

    participant = factory.SubFactory(UserFactory)
    auction = factory.SubFactory(AuctionFactory)


class ItemFactory(DjangoModelFactory):
    class Meta:
        model = Item

    auction = factory.SubFactory(AuctionFactory)
    name = factory.Sequence(lambda n: f"Item {n}")
    base_price = Decimal("100.00")
    bid_step = Decimal("10.00")


class BidFactory(DjangoModelFactory):
    class Meta:
        model = Bid

    bidder = factory.SubFactory(UserFactory)
    item = factory.SubFactory(ItemFactory)
    bid_amount = Decimal("110.00")
