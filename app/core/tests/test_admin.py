from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from core.models import User


@dataclass
class SetupReturn:
    admin_user: User
    client: Client
    user: User


class AdminSiteTests(TestCase):
    def set_up_test(self) -> SetupReturn:
        admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="test123",
        )
        client = Client()

        client.force_login(admin_user)
        user = get_user_model().objects.create_user(
            email="user@example.com",
            password="test123",
            name="Test User",
        )

        return SetupReturn(admin_user=admin_user, client=client, user=user)

    def test_users_are_listed_on_page(self):
        setup = self.set_up_test()
        url = reverse("admin:core_user_changelist")

        res = setup.client.get(url)

        self.assertContains(res, setup.user.name)
        self.assertContains(res, setup.user.email)

    def test_edit_user_page(self):
        setup = self.set_up_test()
        url = reverse("admin:core_user_change", args=[setup.user.id])

        res = setup.client.get(url)

        self.assertEqual(200, res.status_code)

    def test_create_user_page_exists(self):
        setup = self.set_up_test()
        url = reverse("admin:core_user_add")

        res = setup.client.get(url)

        self.assertEqual(200, res.status_code)
