from decimal import Decimal
import pytest
from django.utils import timezone
from datetime import timedelta
from tests.factories import AuctionFactory, ItemFactory, AuctionParticipantFactory


BID_URL = "/api/v1/auctions/{auction_id}/items/{item_id}/bids/"


@pytest.mark.django_db
class TestBidValidation:
    def _url(self, item):
        return BID_URL.format(auction_id=item.auction_id, item_id=item.id)

    def test_participant_can_bid(self, api_client, user, auction, item):
        AuctionParticipantFactory(participant=user, auction=auction)
        api_client.force_authenticate(user)

        response = api_client.post(self._url(item), {"bid_amount": "110.00"})

        assert response.status_code == 201
        assert Decimal(response.data["bid_amount"]) == Decimal("110.00")

    def test_non_participant_cannot_bid_private_auction(
        self, api_client, other_user, item
    ):
        api_client.force_authenticate(other_user)

        response = api_client.post(self._url(item), {"bid_amount": "110.00"})

        assert response.status_code == 404

    def test_auctioneer_cannot_bid_own_auction(self, api_client, auctioneer, item):
        api_client.force_authenticate(auctioneer)

        response = api_client.post(self._url(item), {"bid_amount": "110.00"})

        assert response.status_code == 400
        assert "own auction" in str(response.data).lower()

    def test_bid_below_minimum_rejected(self, api_client, user, auction, item):
        AuctionParticipantFactory(participant=user, auction=auction)
        api_client.force_authenticate(user)

        response = api_client.post(self._url(item), {"bid_amount": "50.00"})

        assert response.status_code == 400

    def test_bid_on_closed_auction_rejected(self, api_client, user, auctioneer):
        auction = AuctionFactory(auctioneer=auctioneer, status="closed")
        item = ItemFactory(auction=auction)
        AuctionParticipantFactory(participant=user, auction=auction)
        api_client.force_authenticate(user)

        response = api_client.post(self._url(item), {"bid_amount": "110.00"})

        assert response.status_code == 400

    def test_bid_past_date_end_rejected(self, api_client, user, auctioneer):
        auction = AuctionFactory(
            auctioneer=auctioneer,
            date_end=timezone.now() - timedelta(hours=1),
        )
        item = ItemFactory(auction=auction)
        AuctionParticipantFactory(participant=user, auction=auction)
        api_client.force_authenticate(user)

        response = api_client.post(self._url(item), {"bid_amount": "110.00"})

        assert response.status_code == 400

    def test_lower_bids_rejected(self, api_client, user, auction, item):
        AuctionParticipantFactory(participant=user, auction=auction)
        api_client.force_authenticate(user)

        first = api_client.post(self._url(item), {"bid_amount": "210.00"})
        assert first.status_code == 201

        second = api_client.post(self._url(item), {"bid_amount": "110.00"})
        assert second.status_code == 400

        item.refresh_from_db()
        assert item.current_price == Decimal("210.00")