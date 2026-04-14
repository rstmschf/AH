import pytest
from tests.factories import AuctionFactory, AuctionParticipantFactory, UserFactory
from auctions.models import Auction, AuctionParticipant
from django.utils import timezone
from datetime import timedelta

AUC_URL_DETAIL = "/api/v1/auctions/{auction_id}/"


@pytest.mark.django_db
class TestAuctionPermissions:
    def _url(self, auction):
        return AUC_URL_DETAIL.format(auction_id=auction.id)
    
    def test_auctioneer_can_edit(self, api_client, auctioneer, auction):
        api_client.force_authenticate(auctioneer)

        response = api_client.patch(self._url(auction), {"is_public": True})

        assert response.status_code == 200
        auction.refresh_from_db()
        assert auction.is_public is True

    def test_other_user_cant_edit_private_auction(self, api_client, user, auction):
        api_client.force_authenticate(user)

        response = api_client.patch(self._url(auction), {"is_public": True})

        assert response.status_code == 404
        auction.refresh_from_db()
        assert auction.is_public is False

    def test_other_user_cant_edit_public_auction(self, api_client, user, public_auction):
        api_client.force_authenticate(user)

        response = api_client.patch(self._url(public_auction), {"is_public": False})

        assert response.status_code == 403
        public_auction.refresh_from_db()
        assert public_auction.is_public is True