import pytest
from django.utils import timezone
from datetime import timedelta
from auctions.models import Auction


AUC_URL = "/api/v1/auctions/"
AUC_URL_DETAIL = "/api/v1/auctions/{auction_id}/"


@pytest.mark.django_db
class TestAuctionViewSet:
    def _url(self, auction):
        return AUC_URL_DETAIL.format(auction_id=auction.id)

    def test_create_sets_auctioneer_and_defaults(self, api_client, user, other_user):
        api_client.force_authenticate(user)

        payload = {
            "name": "Test Sale",
            "description": "Test description",
            "currency": "EUR",
            "date_start": (timezone.now() + timedelta(days=1)).isoformat(),
            "date_end": (timezone.now() + timedelta(days=7)).isoformat(),
            "auctioneer": other_user.id,
        }

        response = api_client.post(AUC_URL, payload)

        assert response.status_code == 201
        auction = Auction.objects.get(id=response.data["id"])

        assert auction.auctioneer == user
        assert auction.auctioneer != other_user
        assert auction.status == "pending"
        assert auction.is_public is False
        assert auction.invite_code
        assert len(auction.invite_code) > 10

    def test_create_auction_rejects_invalid_currency(self, api_client, user):
        api_client.force_authenticate(user)

        payload = {
            "name": "Test Sale",
            "currency": "XXX",
            "date_start": (timezone.now() + timedelta(days=1)).isoformat(),
            "date_end": (timezone.now() + timedelta(days=7)).isoformat(),
        }

        response = api_client.post(AUC_URL, payload)
        assert response.status_code == 400
        assert "currency" in response.data


    def test_create_auction_rejects_missing_name(self, api_client, user):
        api_client.force_authenticate(user)

        payload = {
            "currency": "EUR",
            "date_start": (timezone.now() + timedelta(days=1)).isoformat(),
            "date_end": (timezone.now() + timedelta(days=7)).isoformat(),
        }

        response = api_client.post(AUC_URL, payload)
        assert response.status_code == 400
        assert "name" in response.data

    def test_create_auction_rejects_end_before_start(self, api_client, user):
        api_client.force_authenticate(user)
        now = timezone.now()

        payload = {
            "name": "Test Auction",
            "currency": "EUR",
            "date_start": (now + timedelta(days=7)).isoformat(),
            "date_end": (now + timedelta(days=1)).isoformat(),
        }

        response = api_client.post(AUC_URL, payload)

        assert response.status_code == 400
        assert "date_end" in response.data

    def test_patch_ignores_readonly_fields(self, api_client, auctioneer, auction):
        api_client.force_authenticate(auctioneer)

        response = api_client.patch(
            self._url(auction),
            {"status": "closed", "name": "New Name"},
        )

        assert response.status_code == 200
        auction.refresh_from_db()
        assert auction.name == "New Name"
        assert auction.status == "active"

    def test_patch_updates_specified_fields(self, api_client, auctioneer, auction):
        api_client.force_authenticate(auctioneer)

        response = api_client.patch(
            self._url(auction),
            {"is_public": True, "name": "New Auction Name"},
        )

        assert response.status_code == 200
        auction.refresh_from_db()
        assert auction.is_public is True
        assert auction.name == "New Auction Name"
        assert auction.description == "Test auction"
