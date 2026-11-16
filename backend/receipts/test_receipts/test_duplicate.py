import threading

from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TransactionTestCase
from rest_framework import status
from rest_framework.test import APIClient

from receipts.models import Receipt

User = get_user_model()


class SequentialDuplicateTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user("buyer", password="pass12345")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.url = "/api/receipts/"
        self.payload = {
            "fn": "1234567890123456",
            "fd": "123",
            "fp": "456",
            "purchase_datetime": "2026-06-01T12:00:00",
            "amount": "1500.00",
        }

    def test_second_identical_receipt_returns_400_not_500(self):
        r1 = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)

        r2 = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", r2.data["errors"])
        self.assertEqual(Receipt.objects.count(), 1)


class RaceDuplicateTest(TransactionTestCase):
    """Два параллельных POST одного и того же чека.

    Ожидание: ровно один 201, второй 400 (не 500), в БД одна запись.
    """

    def setUp(self):
        self.user = User.objects.create_user("buyer", password="pass12345")
        self.url = "/api/receipts/"
        self.payload = {
            "fn": "1234567890123456",
            "fd": "123",
            "fp": "456",
            "purchase_datetime": "2026-06-01T12:00:00",
            "amount": "1500.00",
        }

    def test_parallel_duplicate_returns_400(self):
        results = []
        errors = []
        barrier = threading.Barrier(2)

        def post():
            client = APIClient()
            client.force_authenticate(self.user)
            try:
                barrier.wait(timeout=5)
                r = client.post(self.url, self.payload, format="json")
                results.append(r.status_code)
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)
            finally:
                connections.close_all()

        threads = [threading.Thread(target=post) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        self.assertEqual(errors, [], f"threads raised: {errors}")
        self.assertEqual(
            sorted(results),
            [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST],
            f"expected [201, 400], got {results}",
        )
        self.assertEqual(Receipt.objects.count(), 1)
