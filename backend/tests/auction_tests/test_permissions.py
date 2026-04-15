import pytest
from auctions.models import Auction
from django.utils import timezone
from datetime import timedelta


AUC_URL = "/api/v1/auctions/"
AUC_URL_DETAIL = "/api/v1/auctions/{auction_id}/"


@pytest.mark.django_db
class TestAuctionPermissions:
    def _url(self, auction):
        return AUC_URL_DETAIL.format(auction_id=auction.id)

    def test_auctioneer_can_edit_private_auction(self, api_client, auctioneer, auction):
        api_client.force_authenticate(auctioneer)

        response = api_client.patch(self._url(auction), {"is_public": True})

        assert response.status_code == 200
        auction.refresh_from_db()
        assert auction.is_public is True

    def test_auctioneer_can_edit_public_auction(
        self, api_client, public_auction, auction
    ):
        api_client.force_authenticate(public_auction)

        response = api_client.patch(self._url(auction), {"is_public": False})

        assert response.status_code == 200
        auction.refresh_from_db()
        assert auction.is_public is False

    def test_other_user_cant_edit_private_auction(self, api_client, user, auction):
        api_client.force_authenticate(user)

        response = api_client.patch(self._url(auction), {"is_public": True})

        assert response.status_code == 404
        auction.refresh_from_db()
        assert auction.is_public is False

    def test_other_user_cant_edit_public_auction(
        self, api_client, user, public_auction
    ):
        api_client.force_authenticate(user)

        response = api_client.patch(self._url(public_auction), {"is_public": False})

        assert response.status_code == 403
        public_auction.refresh_from_db()
        assert public_auction.is_public is True

    def test_anonymous_cannot_access(self, api_client, public_auction):
        response = api_client.get(self._url(public_auction))
        assert response.status_code in (401, 403)

    def test_auctioneer_can_delete(self, api_client, auctioneer, auction):
        api_client.force_authenticate(auctioneer)
        response = api_client.delete(self._url(auction))
        assert response.status_code == 204
        assert not Auction.objects.filter(id=auction.id).exists()

    def test_other_user_cant_delete(self, api_client, user, public_auction):
        api_client.force_authenticate(user)
        response = api_client.delete(self._url(public_auction))
        assert response.status_code == 403
        assert Auction.objects.filter(id=public_auction.id).exists()

    def test_non_participant_gets_404_on_private(self, api_client, user, auction):
        api_client.force_authenticate(user)
        response = api_client.get(self._url(auction))
        assert response.status_code == 404

    def test_participant_can_view_private(self, api_client, participant, auction):
        api_client.force_authenticate(participant)
        response = api_client.get(self._url(auction))
        assert response.status_code == 200

    def test_anyone_can_view_public(self, api_client, user, public_auction):
        api_client.force_authenticate(user)
        response = api_client.get(self._url(public_auction))
        assert response.status_code == 200

    def test_auctioneer_sees_invite_code(self, api_client, auctioneer, auction):
        api_client.force_authenticate(auctioneer)
        response = api_client.get(self._url(auction))
        assert "invite_code" in response.data

    def test_participant_does_not_see_invite_code(
        self, api_client, participant, auction
    ):
        api_client.force_authenticate(participant)
        response = api_client.get(self._url(auction))
        assert "invite_code" not in response.data

    def test_any_user_can_create_auction(self, api_client, user):
        api_client.force_authenticate(user)
        response = api_client.post(
            AUC_URL,
            {
                "name": "Test Auction",
                "currency": "USD",
                "date_start": (timezone.now() + timedelta(days=1)).isoformat(),
            },
        )
        assert response.status_code == 201
        assert Auction.objects.get(id=response.data["id"]).auctioneer == user
