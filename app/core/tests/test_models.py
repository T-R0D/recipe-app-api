from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def test_create_user_with_email_is_successful(self) -> None:
        email = "test@example.com"
        password = "testpass123"

        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(email, user.email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_is_normalized(self) -> None:
        sample_emails = (
            (
                "test1@EXAMPLE.com",
                "test1@example.com",
            ),
            (
                "Test2@Example.com",
                "Test2@example.com",
            ),
            (
                "TEST3@EXAMPLE.COM",
                "TEST3@example.com",
            ),
            (
                "test4@example.COM",
                "test4@example.com",
            ),
        )

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email, password="sample123"
            )

            self.assertEqual(expected, user.email)

    def test_new_user_without_email_raises_error(self) -> None:
        with self.assertRaises(ValueError) as e:
            get_user_model().objects.create_user(email="", password="test123")

        self.assertEqual("User must have an email address.", str(e.exception))

    def test_create_super_user(self) -> None:
        user = get_user_model().objects.create_superuser(
            email="test@example.com",
            password="test123",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
