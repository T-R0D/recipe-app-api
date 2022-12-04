from typing import Any

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**kwargs: Any) -> AbstractBaseUser:
    return get_user_model().objects.create_user(**kwargs)


class PublicUserAPITests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_user_success(self) -> None:
        # Arrange.
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name",
        }

        # Act.
        res = self.client.post(CREATE_USER_URL, payload)

        # Assert.
        self.assertEqual(status.HTTP_201_CREATED, res.status_code)

        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

        self.assertNotIn("password", res.data)

    def test_user_with_email_exists_error(self) -> None:
        # Arrange.
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name",
        }
        create_user(**payload)

        # Act.
        res = self.client.post(CREATE_USER_URL, payload)

        # Assert.
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)

    def test_password_too_short_error(self) -> None:
        # Arrange.
        payload = {
            "email": "test@example.com",
            "password": "pw",
            "name": "Test Name",
        }

        # Act.
        res = self.client.post(CREATE_USER_URL, payload)

        # Assert.
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)

        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self) -> None:
        # Arrange.
        user_details = {
            "name": "Test Name",
            "email": "test@example.com",
            "password": "test-usere-password123",
        }
        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }

        # Act.
        res = self.client.post(TOKEN_URL, payload)

        # Assert.
        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertIn("token", res.data)

    def test_create_token_bad_credentials(self) -> None:
        # Arrange.
        user_details = {
            "name": "Test Name",
            "email": "test@example.com",
            "password": "test-usere-password123",
        }
        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": "badpass",
        }

        # Act.
        res = self.client.post(TOKEN_URL, payload)

        # Assert.
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)
        self.assertNotIn("token", res.data)

    def test_create_token_blank_password(self) -> None:
        # Arrange.
        user_details = {
            "name": "Test Name",
            "email": "test@example.com",
            "password": "test-usere-password123",
        }
        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": "",
        }

        # Act.
        res = self.client.post(TOKEN_URL, payload)

        # Assert.
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)
        self.assertNotIn("token", res.data)

    def test_retrieve_user_unauthorized(self) -> None:
        # Act.
        res = self.client.get(ME_URL)

        # Assert.
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, res.status_code)


class PrivateUserAPITests(TestCase):
    def setUp(self) -> None:
        self.user = create_user(
            email="test@example.com",
            password="testpass123",
            name="Test Name",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self) -> None:
        # Act.
        res = self.client.get(ME_URL)

        # Assert.
        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertDictEqual(
            {
                "name": self.user.name,
                "email": self.user.email,
            },
            res.data,
        )

    def test_post_me_not_allowed(self) -> None:
        # Act.
        res = self.client.post(ME_URL, {})

        # Assert.
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, res.status_code)

    def test_update_user_profile(self) -> None:
        # Act.
        payload = {"name": "Updated Name", "password": "newpassword123"}

        # Assert.
        res = self.client.patch(ME_URL, payload)

        # Assert.
        self.assertEqual(status.HTTP_200_OK, res.status_code)

        self.user.refresh_from_db()
        self.assertEqual(payload["name"], self.user.name)
        self.assertTrue(self.user.check_password(payload["password"]))
