from rest_framework import viewsets, permissions
from .serializers import BidCreateSerializer, BidListAndDetailSerializer
from .models import Bid

class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.select_related("item", "bidder")
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return BidCreateSerializer
        return BidListAndDetailSerializer
    
    # def perform_create(self, serializer):
    #     item = get_object_or_404(Item, pk=self.kwargs["item_pk"])