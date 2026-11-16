from datetime import datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import serializers

from .models import Receipt

PROMO_TZ = ZoneInfo("Europe/Moscow")


User = get_user_model()


class ReceiptSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_fn(self, value):
        if not value.isdigit() or len(value) != 16:
            raise serializers.ValidationError("ФН должен содержать 16 цифр")
        return value

    def validate_fd(self, value):
        if not value.isdigit() or not (1 <= len(value) <= 10):
            raise serializers.ValidationError("ФД должен содержать от 1 до 10 цифр")
        return value

    def validate_fp(self, value):
        if not value.isdigit() or not (1 <= len(value) <= 10):
            raise serializers.ValidationError("ФП должен содержать от 1 до 10 цифр")
        return value

    def validate_amount(self, value):
        if value < Decimal(1000):
            raise serializers.ValidationError("Сумма должна быть не меньше 1000 Р")
        return value

    def validate_purchase_datetime(self, value):
        if timezone.is_naive(value):
            value = timezone.make_aware(value, PROMO_TZ)

        start_date = datetime.strptime(settings.PROMO_START_DATE, "%Y-%m-%d").date()
        end_date = datetime.strptime(settings.PROMO_END_DATE, "%Y-%m-%d").date()

        start = datetime.combine(start_date, time.min, tzinfo=PROMO_TZ)
        end = datetime.combine(end_date, time.max, tzinfo=PROMO_TZ)

        if not (start <= value <= end):
            raise serializers.ValidationError(
                f"Дата покупки должна входить в период акции: "
                f"{settings.PROMO_START_DATE} - {settings.PROMO_END_DATE} (МСК)"
            )
        return value

    def validate(self, attrs):
        qs = Receipt.objects.filter(fn=attrs["fn"], fd=attrs["fd"], fp=attrs["fp"])
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {"non_field_errors": ["Чек с такими ФН+ФД+ФП уже зарегистрирован."]}
            )
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        try:
            return Receipt.objects.create(
                user=request.user,
                status=Receipt.STATUS_PENDING,
                **validated_data,
            )
        except IntegrityError:
            raise serializers.ValidationError(
                {"non_field_errors": ["Чек с такими ФН+ФД+ФП уже зарегистрирован."]}
            )

    class Meta:
        model = Receipt
        fields = [
            "id",
            "fn",
            "fd",
            "fp",
            "purchase_datetime",
            "amount",
            "status",
            "status_display",
            "rejection_reason",
            "created_at",
        ]
        read_only_fields = ["status", "rejection_reason", "created_at"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "password_confirm"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Пароли не совпадают."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        return User.objects.create_user(**validated_data)
