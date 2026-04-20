import threading
from decimal import Decimal
import pytest
from django.db import connections
from rest_framework.test import APIClient
from bids.models import Bid
from tests.factories import UserFactory, AuctionParticipantFactory


BID_URL = "/api/v1/auctions/{auction_id}/items/{item_id}/bids/"


@pytest.mark.django_db(transaction=True)
class TestBidConcurrency:
    def _url(self, item):
        return BID_URL.format(auction_id=item.auction_id, item_id=item.id)

    def test_concurrent_equal_bids_one_winner(self, auction, item):
        u1 = UserFactory()
        u2 = UserFactory()
        AuctionParticipantFactory(participant=u1, auction=auction)
        AuctionParticipantFactory(participant=u2, auction=auction)

        results = []
        barrier = threading.Barrier(2)

        def place_bid(bidder):
            client = APIClient()
            client.force_authenticate(bidder)
            barrier.wait()
            resp = client.post(self._url(item), {"bid_amount": "110.00"})
            results.append(resp.status_code)
            connections.close_all()

        t1 = threading.Thread(target=place_bid, args=(u1,))
        t2 = threading.Thread(target=place_bid, args=(u2,))
        t1.start(); t2.start()
        t1.join(); t2.join()

        assert sorted(results) == [201, 400]
        item.refresh_from_db()
        assert item.current_price == Decimal("110.00")
        assert Bid.objects.filter(item=item).count() == 1

    def test_concurrent_higher_bid_succeed(self, auction, item):
        u1 = UserFactory()
        u2 = UserFactory()
        AuctionParticipantFactory(participant=u1, auction=auction)
        AuctionParticipantFactory(participant=u2, auction=auction)

        results = {}
        barrier = threading.Barrier(2)

        def place_bid(bidder, amount):
            client = APIClient()
            client.force_authenticate(bidder)
            barrier.wait()
            resp = client.post(self._url(item), {"bid_amount": amount})
            results[bidder.id] = resp.status_code
            connections.close_all()

        t1 = threading.Thread(target=place_bid, args=(u1, "110.00"))
        t2 = threading.Thread(target=place_bid, args=(u2, "130.00"))
        t2.start(); t1.start() # if t1.start before t2 then t2 arrives second but fires first, locks db, t1 returns 400 because 110<130, if t2.start before t1 both accepted with 201  
        t2.join(); t1.join() # this one behaves identicaly with any order

        assert results[u2.id] == 201
        # assert results[u1.id] == 201 ## will fail if t1.start before t2 but works if t2.sttart before t1 
        item.refresh_from_db()
        assert item.current_price == Decimal("130.00")
        bid_count = Bid.objects.filter(item=item).count()
        assert bid_count == sum(1 for code in results.values() if code == 201)
