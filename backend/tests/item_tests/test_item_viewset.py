import pytest
from decimal import Decimal
from items.models import Item
from tests.factories import ItemFactory, AuctionParticipantFactory

ITEM_URL = "/api/v1/auctions/{auction_id}/items/"
ITEM_URL_DETAIL = "/api/v1/auctions/{auction_id}/items/{item_id}/"


@pytest.mark.django_db
class TestItemViewSet:
    def _detail_url(self, item):
        return ITEM_URL_DETAIL.format(auction_id=item.auction_id, item_id=item.id)

    def _list_url(self, auction):
        return ITEM_URL.format(auction_id=auction.id)

    def test_auctioneer_can_create_item(self, api_client, auctioneer, auction):
        api_client.force_authenticate(auctioneer)

        payload = {
            "name": "New Item",
            "base_price": "50.00",
            "description": "Nice thing",
            "bid_step": "5.00",
        }
        response = api_client.post(self._list_url(auction), payload)

        assert response.status_code == 201
        item = Item.objects.get(id=response.data["id"])
        assert item.auction == auction
        assert item.name == "New Item"
        assert item.base_price == Decimal("50.00")

    def test_non_auctioneer_cannot_create_item(self, api_client, user, auction):
        AuctionParticipantFactory(participant=user, auction=auction)
        api_client.force_authenticate(user)

        payload = {"name": "Item", "base_price": "50.00", "bid_step": "5.00"}
        response = api_client.post(self._list_url(auction), payload)

        assert response.status_code == 403
        assert not Item.objects.filter(name="Item").exists()

    def test_create_rejects_missing_required_fields(
        self, api_client, auctioneer, auction
    ):
        api_client.force_authenticate(auctioneer)

        response = api_client.post(self._list_url(auction), {"name": "No Price"})

        assert response.status_code == 400
        assert "base_price" in response.data

    def test_auctioneer_can_patch_item(self, api_client, auctioneer, item):
        api_client.force_authenticate(auctioneer)

        response = api_client.patch(
            self._detail_url(item),
            {"name": "Updated", "description": "New desc"},
        )

        assert response.status_code == 200
        item.refresh_from_db()
        assert item.name == "Updated"
        assert item.description == "New desc"

    def test_patch_ignores_readonly_fields(self, api_client, auctioneer, item):
        api_client.force_authenticate(auctioneer)
        original_price = item.current_price

        response = api_client.patch(
            self._detail_url(item),
            {"current_price": "9999.00", "won_by": auctioneer.id, "name": "Renamed"},
        )

        assert response.status_code == 200
        item.refresh_from_db()
        assert item.name == "Renamed"
        assert item.current_price == original_price
        assert item.won_by is None

    def test_participant_cannot_patch_item(self, api_client, user, item):
        AuctionParticipantFactory(participant=user, auction=item.auction)
        api_client.force_authenticate(user)

        response = api_client.patch(self._detail_url(item), {"name": "Hacked"})

        assert response.status_code == 403
        item.refresh_from_db()
        assert item.name != "Hacked"

    def test_auctioneer_can_delete_item(self, api_client, auctioneer, item):
        api_client.force_authenticate(auctioneer)

        response = api_client.delete(self._detail_url(item))

        assert response.status_code == 204
        assert not Item.objects.filter(id=item.id).exists()

    def test_participant_cannot_delete_item(self, api_client, user, item):
        AuctionParticipantFactory(participant=user, auction=item.auction)
        api_client.force_authenticate(user)

        response = api_client.delete(self._detail_url(item))

        assert response.status_code == 403
        assert Item.objects.filter(id=item.id).exists()

    def test_list_public_auction_items_visible_to_anyone(
        self, api_client, user, public_auction
    ):
        ItemFactory(auction=public_auction)
        ItemFactory(auction=public_auction)
        api_client.force_authenticate(user)

        response = api_client.get(self._list_url(public_auction))

        assert response.status_code == 200
        assert len(response.data["results"]) == 2

    def test_non_participant_cannot_see_private_auction_items(
        self, api_client, other_user, item
    ):
        api_client.force_authenticate(other_user)

        response = api_client.get(self._list_url(item.auction))

        assert response.status_code == 200
        assert response.data["results"] == []

    def test_participant_sees_private_auction_items(self, api_client, user, item):
        AuctionParticipantFactory(participant=user, auction=item.auction)
        api_client.force_authenticate(user)

        response = api_client.get(self._list_url(item.auction))

        assert response.status_code == 200
        ids = [i["id"] for i in response.data["results"]]
        assert item.id in ids

    def test_non_participant_retrieve_returns_404(self, api_client, other_user, item):
        api_client.force_authenticate(other_user)

        response = api_client.get(self._detail_url(item))

        assert response.status_code == 404

    def test_anonymous_cannot_list(self, api_client, auction):
        response = api_client.get(self._list_url(auction))
        assert response.status_code == 401
