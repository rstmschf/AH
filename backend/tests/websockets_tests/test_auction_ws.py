import pytest
from asgiref.sync import sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from bids.urls import websocket_urlpatterns
from bids.ws_auth import JWTAuthMiddleware


ws_application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))

WS_URL = "/ws/auctions/{auction_id}/"
WS_URL_AUTH = "/ws/auctions/{auction_id}/?token={token}"
BID_URL = "/api/v1/auctions/{auction_id}/items/{item_id}/bids/"


@pytest.mark.django_db(transaction=True)
class TestAuctionWebSocket:
    async def test_anonymous_rejected(self, auction):
        communicator = WebsocketCommunicator(
            ws_application,
            WS_URL.format(auction_id=auction.id),
        )
        connected, code = await communicator.connect()
        assert not connected
        assert code == 4401

    async def test_non_participant_rejected(self, auction, user):
        token = str(AccessToken.for_user(user))
        communicator = WebsocketCommunicator(
            ws_application,
            WS_URL_AUTH.format(auction_id=auction.id, token=token),
        )
        connected, code = await communicator.connect()
        assert not connected
        assert code == 4403

    async def test_participant_connects(self, auction, participant):
        token = str(AccessToken.for_user(participant))
        communicator = WebsocketCommunicator(
            ws_application,
            WS_URL_AUTH.format(auction_id=auction.id, token=token),
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.disconnect()

    async def test_bid_broadcasts(self, auction, item, participant):
        token = str(AccessToken.for_user(participant))
        communicator = WebsocketCommunicator(
            ws_application,
            WS_URL_AUTH.format(auction_id=auction.id, token=token),
        )
        connected, _ = await communicator.connect()
        assert connected

        def place_bid():
            client = APIClient()
            client.force_authenticate(participant)
            return client.post(
                BID_URL.format(auction_id=auction.id, item_id=item.id),
                {"bid_amount": "110.00"},
            )

        response = await sync_to_async(place_bid)()
        assert response.status_code == 201

        event = await communicator.receive_json_from(timeout=2)
        assert event["amount"] == "110.00"
        assert event["bidder"] == participant.username
        assert event["current_price"] == "110.00"

        await communicator.disconnect()

    async def test_bid_broadcasts_to_all_participants(
        self, auction, item, auctioneer, participant
    ):
        t_auc = str(AccessToken.for_user(auctioneer))
        t_par = str(AccessToken.for_user(participant))

        c_auc = WebsocketCommunicator(
            ws_application,
            WS_URL_AUTH.format(auction_id=auction.id, token=t_auc),
        )
        c_par = WebsocketCommunicator(
            ws_application,
            WS_URL_AUTH.format(auction_id=auction.id, token=t_par),
        )
        await c_auc.connect()
        await c_par.connect()

        def place_bid():
            client = APIClient()
            client.force_authenticate(participant)
            return client.post(
                BID_URL.format(auction_id=auction.id, item_id=item.id),
                {"bid_amount": "110.00"},
            )

        await sync_to_async(place_bid)()

        event_auc = await c_auc.receive_json_from(timeout=2)
        event_par = await c_par.receive_json_from(timeout=2)
        assert event_auc["amount"] == event_par["amount"] == "110.00"

        await c_auc.disconnect()
        await c_par.disconnect()