from django.urls import path, include
from rest_framework_nested import routers
from .views import AuctionViewSet
from items.views import ItemViewSet, ItemImageViewSet
from bids.views import BidViewSet

router = routers.DefaultRouter()
router.register(r"", AuctionViewSet, basename="auction")

items_router = routers.NestedDefaultRouter(router, r"", lookup="auction")
items_router.register(r"items", ItemViewSet, basename="auction-items")

images_router = routers.NestedDefaultRouter(items_router, r"items", lookup="item")
images_router.register(r"images", ItemImageViewSet, basename="item-images")

bids_router = routers.NestedDefaultRouter(items_router, r"items", lookup="item")
bids_router.register(r"bids", BidViewSet, basename="item-bids")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(items_router.urls)),
    path("", include(images_router.urls)),
    path("", include(bids_router.urls)),
]