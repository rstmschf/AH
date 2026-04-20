from rest_framework import permissions


class IsAuctioneerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, "auctioneer_id"):
            auction = obj
        elif hasattr(obj, "auction"):
            auction = obj.auction
        elif hasattr(obj, "item"):
            auction = obj.item.auction
        else:
            return False
        return auction.auctioneer_id == request.user.id
