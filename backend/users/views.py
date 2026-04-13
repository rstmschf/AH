from .serializers import (
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    RegisterSerializer,
)
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = User.objects.prefetch_related(
            "auctions_created", "items_won", "bids", "participant_at"
        ).get(pk=self.request.user.pk)
        return obj


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = User.objects.prefetch_related(
            "auctions_created", "items_won", "bids", "participant_at"
        ).filter(is_deleted=False, is_hidden=False)
        return queryset


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer