from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db.models import Q
from auctions.models import Auction


class AuctionConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close(code=4401)
            return

        self.auction_id = int(self.scope["url_route"]["kwargs"]["auction_id"])
        if not await self._can_view(user, self.auction_id):
            await self.close(code=4403)
            return

        self.group = f"auction_{self.auction_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group"):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def new_bid(self, event):
        await self.send_json(event["payload"])

    @staticmethod
    @database_sync_to_async
    def _can_view(user, auction_id):
        return Auction.objects.filter(
            Q(pk=auction_id)
            & (Q(is_public=True) | Q(auctioneer=user) | Q(participants=user))
        ).exists()