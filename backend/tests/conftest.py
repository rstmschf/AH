import pytest
from rest_framework.test import APIClient
from tests.factories import (
    UserFactory,
    AuctionFactory,
    AuctionParticipantFactory,
    ItemFactory,
    BidFactory,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def auctioneer(db):
    return UserFactory()


@pytest.fixture
def other_user(db):
    return UserFactory()


@pytest.fixture
def auction(db, auctioneer):
    return AuctionFactory(auctioneer=auctioneer)


@pytest.fixture
def public_auction(db, auctioneer):
    return AuctionFactory(auctioneer=auctioneer, is_public=True)


@pytest.fixture
def participant(db, user, auction):
    AuctionParticipantFactory(participant=user, auction=auction)
    return user


@pytest.fixture
def item(db, auction):
    return ItemFactory(auction=auction)


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def auctioneer_client(api_client, auctioneer):
    api_client.force_authenticate(user=auctioneer)
    return api_client


CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
