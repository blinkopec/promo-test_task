from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class RegistrationTest(TestCase):
    url = "/api/auth/register/"

    def test_register_success_creates_user_and_logs_in(self):
        client = APIClient()
        r = client.post(
            self.url,
            {
                "username": "newbuyer",
                "password": "StrongPass123",
                "password_confirm": "StrongPass123",
            },
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newbuyer").exists())
        me = client.get("/api/auth/me/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["username"], "newbuyer")

    def test_register_duplicate_username_rejected(self):
        User.objects.create_user("taken", password="pass12345")
        r = APIClient().post(
            self.url,
            {
                "username": "taken",
                "password": "StrongPass123",
                "password_confirm": "StrongPass123",
            },
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", r.data)

    def test_register_password_mismatch_rejected(self):
        r = APIClient().post(
            self.url,
            {
                "username": "newbuyer",
                "password": "StrongPass123",
                "password_confirm": "DifferentPass123",
            },
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password_rejected(self):
        r = APIClient().post(
            self.url,
            {
                "username": "newbuyer",
                "password": "123",
                "password_confirm": "123",
            },
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
