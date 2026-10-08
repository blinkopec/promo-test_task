from datetime import datetime, time

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from .models import Receipt


class ReceiptSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

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
        if value < 1000:
            raise serializers.ValidationError("Сумма должна быть не меньше 1000 Р")
        return value

    def validate_purchase_datetime(self, value):
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.get_current_timezone())

        start_date = datetime.strptime(settings.PROMO_START_DATE, "%Y-%m-%d").date()
        end_date = datetime.strptime(settings.PROMO_END_DATE, "%Y-%m-%d").date()

        start = timezone.make_aware(
            datetime.combine(start_date, time.min),
            timezone.get_current_timezone(),
        )

        end = timezone.make_aware(
            datetime.combine(end_date, time.max),
            timezone.get_current_timezone(),
        )

        if not (start <= value <= end):
            raise serializers.ValidationError(
                f"Дата покупки должна входить в период акции: "
                f"{settings.PROMO_START_DATE} - {settings.PROMO_END_DATE}"
            )
        return value
    
    def create(self, validated_data):
        request = self.context['request']
        return Receipt.objects.create(
            user=request.user,
            status=Receipt.STATUS_PENDING,
            **validated_data,
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
