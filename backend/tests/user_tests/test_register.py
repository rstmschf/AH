import pytest
from django.contrib.auth import get_user_model

User = get_user_model()
REGISTER_URL = "/api/v1/auth/register/"


@pytest.mark.django_db
class TestRegister:
    def _payload(self, **overrides):
        data = {
            "username": "newuser",
            "email": "newuser@mail.com",
            "password": "NewPass123!",
            "password_confirm": "NewPass123!",
        }
        data.update(overrides)
        return data

    def test_register_creates_user(self, api_client):
        response = api_client.post(REGISTER_URL, self._payload())

        assert response.status_code == 201
        user = User.objects.get(username="newuser")
        assert user.email == "newuser@mail.com"
        assert user.check_password("NewPass123!")

    def test_register_does_not_return_password(self, api_client):
        response = api_client.post(REGISTER_URL, self._payload())

        assert response.status_code == 201
        assert "password" not in response.data
        assert "password_confirm" not in response.data

    def test_register_rejects_mismatched_passwords(self, api_client):
        response = api_client.post(
            REGISTER_URL,
            self._payload(password_confirm="DifferentPass123!"),
        )

        assert response.status_code == 400
        assert "password_confirm" in response.data
        assert not User.objects.filter(username="newuser").exists()

    def test_register_rejects_short_password(self, api_client):
        response = api_client.post(
            REGISTER_URL,
            self._payload(password="short", password_confirm="short"),
        )

        assert response.status_code == 400
        assert "password" in response.data

    def test_register_rejects_duplicate_username(self, api_client, user):
        response = api_client.post(
            REGISTER_URL,
            self._payload(username=user.username),
        )

        assert response.status_code == 400
        assert "username" in response.data

    def test_register_rejects_missing_fields(self, api_client):
        response = api_client.post(REGISTER_URL, {"username": "onlyname"})

        assert response.status_code == 400
        assert "password" in response.data
        assert "email" in response.data

    def test_register_is_public(self, api_client):
        response = api_client.post(REGISTER_URL, self._payload())
        assert response.status_code == 201