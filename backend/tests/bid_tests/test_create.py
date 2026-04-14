import pytest
from tests.factories import AuctionParticipantFactory
from bids.models import Bid


BID_URL = "/api/v1/auctions/{auction_id}/items/{item_id}/bids/"


@pytest.mark.django_db
class TestBidCreate:
    def _url(self, item):
        return BID_URL.format(auction_id=item.auction_id, item_id=item.id)

    def test_bidder_set_from_request(self, api_client, user, auction, item):
        AuctionParticipantFactory(participant=user, auction=auction)
        api_client.force_authenticate(user)

        response = api_client.post(self._url(item), {"bid_amount": "110.00"})
        assert response.status_code == 201

        bid = Bid.objects.get(id=response.data["id"])
        assert bid.bidder == user

    def test_bids_update_current_price(self, api_client, user, auction, item):
        AuctionParticipantFactory(participant=user, auction=auction)
        api_client.force_authenticate(user)

        response = api_client.post(self._url(item), {"bid_amount": "110.00"})
        assert response.status_code == 201

        response = api_client.post(self._url(item), {"bid_amount": "210.00"})
        assert response.status_code == 201

        bid = Bid.objects.get(id=response.data["id"])
        item.refresh_from_db()
        assert item.current_price == bid.bid_amount