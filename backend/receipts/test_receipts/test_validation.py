from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from receipts.models import Receipt
from receipts.serializers import PROMO_TZ

User = get_user_model()


class ReceiptValidationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("buyer", password="pass12345")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.url = "/api/receipts/"

    def _payload(self, **overrides):
        data = {
            "fn": "1234567890123456",
            "fd": "123",
            "fp": "456",
            "purchase_datetime": "2026-06-01T12:00:00",
            "amount": "1500.00",
        }
        data.update(overrides)
        return data

    def test_fn_wrong_length_rejected(self):
        for bad in ("123456789012345", "12345678901234567"):
            with self.subTest(fn=bad):
                r = self.client.post(self.url, self._payload(fn=bad), format="json")
                self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("fn", r.data["errors"])

    def test_fn_non_digit_rejected(self):
        r = self.client.post(
            self.url, self._payload(fn="12345678901234ab"), format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("fn", r.data["errors"])

    def test_fd_fp_boundaries_accepted(self):
        for fd in ("1", "1234567890"):
            for fp in ("1", "1234567890"):
                with self.subTest(fd=fd, fp=fp):
                    r = self.client.post(
                        self.url, self._payload(fd=fd, fp=fp), format="json"
                    )
                    self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_fd_fp_empty_and_too_long_rejected(self):
        for bad in ("", "12345678901"):
            with self.subTest(fd=bad):
                r = self.client.post(self.url, self._payload(fd=bad), format="json")
                self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("fd", r.data["errors"])
            with self.subTest(fp=bad):
                r = self.client.post(self.url, self._payload(fp=bad), format="json")
                self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("fp", r.data["errors"])

    def test_amount_below_min_rejected(self):
        r = self.client.post(self.url, self._payload(amount="999.99"), format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", r.data["errors"])

    def test_amount_exactly_1000_accepted(self):
        r = self.client.post(self.url, self._payload(amount="1000.00"), format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_promo_tz_is_moscow(self):
        self.assertEqual(str(PROMO_TZ), "Europe/Moscow")

    def test_purchase_at_start_boundary_msk_accepted(self):
        start_date = datetime.strptime(settings.PROMO_START_DATE, "%Y-%m-%d").date()
        dt = datetime.combine(start_date, time.min, tzinfo=PROMO_TZ)
        r = self.client.post(
            self.url,
            self._payload(purchase_datetime=dt.isoformat()),
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_purchase_at_end_boundary_msk_accepted(self):
        end_date = datetime.strptime(settings.PROMO_END_DATE, "%Y-%m-%d").date()
        dt = datetime.combine(end_date, time.max, tzinfo=PROMO_TZ)
        r = self.client.post(
            self.url,
            self._payload(purchase_datetime=dt.isoformat()),
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_purchase_before_start_msk_rejected(self):
        start_date = datetime.strptime(settings.PROMO_START_DATE, "%Y-%m-%d").date()
        dt = datetime.combine(start_date, time.min, tzinfo=PROMO_TZ)
        dt = dt - timedelta(seconds=1)
        r = self.client.post(
            self.url,
            self._payload(purchase_datetime=dt.isoformat()),
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("purchase_datetime", r.data["errors"])

    def test_purchase_after_end_msk_rejected(self):
        end_date = datetime.strptime(settings.PROMO_END_DATE, "%Y-%m-%d").date()
        dt = datetime.combine(end_date, time.max, tzinfo=PROMO_TZ)
        dt = dt + timedelta(seconds=1)
        r = self.client.post(
            self.url,
            self._payload(purchase_datetime=dt.isoformat()),
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("purchase_datetime", r.data["errors"])

    def test_naive_datetime_treated_as_moscow(self):
        start_date = datetime.strptime(settings.PROMO_START_DATE, "%Y-%m-%d").date()
        naive = datetime.combine(start_date, time.min).isoformat()
        r = self.client.post(
            self.url,
            self._payload(purchase_datetime=naive),
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_utc_datetime_converted_to_moscow(self):
        start_date = datetime.strptime(settings.PROMO_START_DATE, "%Y-%m-%d").date()
        utc_dt = datetime.combine(start_date, time.min, tzinfo=PROMO_TZ)
        utc_dt = utc_dt.astimezone(ZoneInfo("UTC"))
        r = self.client.post(
            self.url,
            self._payload(purchase_datetime=utc_dt.isoformat()),
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_new_receipt_is_pending(self):
        r = self.client.post(self.url, self._payload(), format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        receipt = Receipt.objects.get()
        self.assertEqual(receipt.status, Receipt.STATUS_PENDING)
        self.assertEqual(receipt.user_id, self.user.id)
