from tests.base_test_case import BaseTestCase


class userTests(BaseTestCase):
    def test_register(self):
        # Register a user
        response = self.client.post("/users", json={
            "name": "user1",
            "email": "user@example.com",
            "password": "testing123"
        })
        print("response is", dir(response))
        print(response.json)
        assert response.status_code == 201

        # Again try registering from the same email
        response = self.client.post("/users", json={
            "name": "user2",
            "email": "user@example.com",
            "password": "testing123"
        })
        assert response.status_code == 400
