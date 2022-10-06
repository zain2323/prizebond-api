from tests.base_test_case import BaseTestCase
from api.models import Token


class AuthTests(BaseTestCase):
    def test_no_auth(self):
        response = self.client.get("/users")
        assert response.status_code == 401

    def test_get_token(self):
        # First registering a user
        user = self.register_user("user", "user@example.com")
        assert user.status_code == 201
        # Now getting the token
        token = self.client.post(
            "/tokens", auth=("user@example.com", "testing123"))
        assert token.status_code == 200
        access_token = token.json["access_token"]
        refresh_token = token.json["refresh_token"]

        assert access_token is not None
        assert refresh_token is not None

        # Now verifying if the token is valid
        current_user = self.client.get("/about", headers={
            'Authorization': f"Bearer {access_token}"
        })
        assert current_user.status_code == 200
        assert current_user.json["name"] == "user"
        assert current_user.json["email"] == "user@example.com"

        # Now verifying if the authentication fails if
        # user tries to provide invalid credentials
        token = self.client.post(
            "/tokens", auth=("user2@example.com", "testing1231"))
        assert token.status_code == 403

    def test_revoke_token(self):
        # First registering a user
        user = self.register_user("user", "user@example.com")
        assert user.status_code == 201
        # Now getting the token
        token = self.client.post(
            "/tokens", auth=("user@example.com", "testing123"))
        assert token.status_code == 200
        access_token = token.json["access_token"]
        refresh_token = token.json["refresh_token"]

        assert access_token is not None
        assert refresh_token is not None

        # Now revoking the token
        response = self.client.delete("/tokens", headers={
            "Authorization": f"Bearer {access_token}"
        })
        assert response.status_code == 204

        # make sure token is expired
        token = Token.query.filter_by(
            access_token=access_token, refresh_token=refresh_token).first()
        assert token.is_expired()

    def test_refresh_token(self):
        # First registering a user
        user = self.register_user("user", "user@example.com")
        assert user.status_code == 201
        # Now getting the token
        token = self.client.post(
            "/tokens", auth=("user@example.com", "testing123"))
        assert token.status_code == 200
        access_token = token.json["access_token"]
        refresh_token = token.json["refresh_token"]

        assert access_token is not None
        assert refresh_token is not None

        # Now refreshing the token
        token = self.client.put("/tokens", json={
            "access_token": access_token,
            "refresh_token": refresh_token
        })
        assert token.status_code == 200
        assert token.json["access_token"] is not None
        assert token.json["refresh_token"] is not None

        # verifying if the old access token is expired
        token_db = Token.query.filter_by(
            access_token=access_token, refresh_token=refresh_token).first()
        assert token_db.is_expired()
