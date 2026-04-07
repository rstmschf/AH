from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MeView, UserProfileView, RegisterView, CustomTokenObtainPairView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("users/<int:pk>/", UserProfileView.as_view(), name="user-profile"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login")
]
