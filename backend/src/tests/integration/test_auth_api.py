from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from src.models import User


class AuthAPITests(TestCase):
    # Shared Arrange: API client and an existing user account.
    def setUp(self):
        self.client = APIClient()
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password=self.password,
            full_name="Pet Owner",
        )

    def login(self, username="owner", password=None):
        return self.client.post(
            reverse("login"),
            {
                "username": username,
                "password": password or self.password,
            },
            format="json",
        )

    def test_register_creates_pet_owner_user(self):
        # Act
        response = self.client.post(
            reverse("register"),
            {
                "username": "new_owner",
                "email": "new-owner@example.com",
                "password": "AnotherStrongPass123!",
                "full_name": "New Pet Owner",
                "phone": "0900000000",
                "address": "123 Street",
            },
            format="json",
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["username"], "new_owner")
        self.assertEqual(response.data["data"]["role"], User.ROLE_PET_OWNER)
        self.assertNotIn("password", response.data["data"])
        self.assertTrue(User.objects.filter(username="new_owner").exists())

    def test_login_returns_tokens_and_user_data(self):
        # Act
        response = self.login()

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("access_token", response.data["data"])
        self.assertIn("refresh_token", response.data["data"])
        self.assertEqual(response.data["data"]["user"]["username"], self.user.username)

    def test_profile_without_token_is_rejected(self):
        # Act
        response = self.client.get(reverse("profile"))

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])

    def test_profile_with_access_token_returns_current_user(self):
        # Arrange
        login_response = self.login()
        access_token = login_response.data["data"]["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Act
        response = self.client.get(reverse("profile"))

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["id"], self.user.id)
        self.assertEqual(response.data["data"]["username"], self.user.username)
