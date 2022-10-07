from tests.base_test_case import BaseTestCase
from api.models import User


class UserTests(BaseTestCase):
    def test_register(self):
        # Register a user
        user = self.register_user("user", "user@example.com")
        assert user.status_code == 201

        # Again try registering from the same email
        user = self.register_user("user", "user@example.com")
        assert user.status_code == 400

        # Registering from a different email now
        another = self.register_user("another", "another@example.com")
        assert another.status_code == 201

        # make sure the registered users are in database
        user = User.query.filter_by(email="user@example.com").first()
        assert user is not None
        assert user.email == "user@example.com"

    def test_retrieve_all_users(self):
        # Registering a new user
        user1 = self.register_user("user1", "user1@example.com")
        user2 = self.register_user("user2", "user2@example.com")
        assert user1.status_code == 201
        assert user2.status_code == 201
        # Retrieving the token
        token = self.client.post(
            "/tokens", auth=("user1@example.com", "testing123"))
        assert token.status_code == 200
        access_token = token.json["access_token"]
        assert access_token is not None
        # Verifying if the endpoint /users work as expected
        users = self.client.get("/users", headers={
            "Authorization": f"Bearer {access_token}"
        })
        assert users.status_code == 200
        # Verifies that all users are returned
        assert len(users.json) == 4

    def test_get_user_id(self):
        # Retrieving the token
        token = self.client.post(
            "/tokens", auth=("testuser1@email.com", "testing123"))
        assert token.status_code == 200
        access_token = token.json["access_token"]

        user = self.client.get("/user/2", headers={
            "Authorization": f"Bearer {access_token}"
        })

        assert user.status_code == 200
        assert user.json["id"] == 2
        assert user.json["email"] == "testuser2@email.com"

    def test_update_user(self):
        # First registering a new user
        user = self.register_user("zain", "zain@email.com")
        assert user.status_code == 201

        # Retrieving the token
        token = self.client.post(
            "/tokens", auth=("zain@email.com", "testing123"))
        assert token.status_code == 200
        access_token = token.json["access_token"]

        # Now updating the user
        updated_user = self.client.put("/about", headers={
            "Authorization": f"Bearer {access_token}"
        }, json={
            "name": "zain siddiqui",
            "email": "zainsiddiqui@email.com"
        })

        assert updated_user.status_code == 200
        assert updated_user.json["name"] == 'zain siddiqui'
        assert updated_user.json["email"] == 'zainsiddiqui@email.com'
