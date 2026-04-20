from django.urls import path
from .consumers import AuctionConsumer

urlpatterns = []

websocket_urlpatterns = [
    path("ws/auctions/<int:auction_id>/", AuctionConsumer.as_asgi()),
]