import pytest
from tests.factories import AuctionFactory, AuctionParticipantFactory, BidFactory, ItemFactory

ME_URL = "/api/v1/auth/me/"


@pytest.mark.django_db
class TestMe:
    def test_anonymous_cannot_access_me(self, api_client):
        response = api_client.get(ME_URL)
        assert response.status_code == 401

    def test_me_returns_current_user(self, api_client, user):
        api_client.force_authenticate(user)

        response = api_client.get(ME_URL)

        assert response.status_code == 200
        assert response.data["username"] == user.username
        assert response.data["email"] == user.email

    def test_me_does_not_leak_password(self, api_client, user):
        api_client.force_authenticate(user)

        response = api_client.get(ME_URL)

        assert "password" not in response.data

    def test_me_includes_related_collections(self, api_client, user, auction):
        created = AuctionFactory(auctioneer=user)
        AuctionParticipantFactory(participant=user, auction=auction)
        item = ItemFactory(auction=auction)
        bid = BidFactory(bidder=user, item=item)
        api_client.force_authenticate(user)

        response = api_client.get(ME_URL)

        assert response.status_code == 200
        assert created.id in response.data["auctions_created"]
        assert auction.id in response.data["participated_auctions"]
        assert bid.id in response.data["bids"]

    def test_me_patch_updates_profile(self, api_client, user):
        api_client.force_authenticate(user)

        response = api_client.patch(
            ME_URL,
            {"first_name": "Jane", "last_name": "Doe"},
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.first_name == "Jane"
        assert user.last_name == "Doe"

    def test_me_patch_updates_email(self, api_client, user):
        api_client.force_authenticate(user)

        response = api_client.patch(ME_URL, {"email": "new@mail.com"})

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.email == "new@mail.com"

    def test_me_returns_only_own_data(self, api_client, user, other_user):
        AuctionFactory(auctioneer=other_user)
        api_client.force_authenticate(user)

        response = api_client.get(ME_URL)

        assert response.status_code == 200
        assert response.data["username"] == user.username
        assert response.data["auctions_created"] == []