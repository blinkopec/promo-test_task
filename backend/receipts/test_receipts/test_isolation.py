from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from receipts.models import Receipt

User = get_user_model()


class ReceiptIsolationTest(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.bob = User.objects.create_user("bob", password="pass12345")

        self.alice_receipt = Receipt.objects.create(
            user=self.alice,
            fn="1111111111111111",
            fd="1",
            fp="1",
            purchase_datetime="2026-06-01T12:00:00+03:00",
            amount="1500.00",
            status=Receipt.STATUS_PENDING,
        )
        self.bob_receipt = Receipt.objects.create(
            user=self.bob,
            fn="2222222222222222",
            fd="2",
            fp="2",
            purchase_datetime="2026-06-02T12:00:00+03:00",
            amount="2000.00",
            status=Receipt.STATUS_PENDING,
        )

    def test_user_sees_only_own_receipts(self):
        client = APIClient()
        client.force_authenticate(self.alice)
        r = client.get("/api/receipts/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in r.data["results"]]
        self.assertEqual(ids, [self.alice_receipt.id])

    def test_anonymous_cannot_list(self):
        r = APIClient().get("/api/receipts/")
        self.assertIn(
            r.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_user_cannot_create_for_other_user(self):
        client = APIClient()
        client.force_authenticate(self.alice)
        r = client.post(
            "/api/receipts/",
            {
                "fn": "3333333333333333",
                "fd": "3",
                "fp": "3",
                "purchase_datetime": "2026-06-03T12:00:00",
                "amount": "1500.00",
                "user": self.bob.id,
            },
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        created = Receipt.objects.get(fn="3333333333333333")
        self.assertEqual(created.user_id, self.alice.id)
