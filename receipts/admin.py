from django import forms
from django.contrib import admin

from .models import Receipt


class ReceiptAdminForm(forms.ModelForm):
    def clean(self):
        cleaned = super().clean()
        if cleaned.get("status") == Receipt.STATUS_REJECTED and not cleaned.get(
            "rejection_reason"
        ):
            self.add_error("rejection_reason", "Укажите причину отказа")

        return cleaned

    class Meta:
        model = Receipt
        fields = "__all__"


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    form = ReceiptAdminForm
    list_display = (
        "id",
        "user",
        "fn",
        "fd",
        "fp",
        "purchase_datetime",
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("fn", "fd", "fp", "user__username")
    readonly_fields = ("created_at",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "fn",
                    "fd",
                    "fp",
                    "purchase_datetime",
                    "amount",
                    "status",
                    "rejection_reason",
                )
            },
        ),
        ("Служебное", {"fields": ("created_at",)}),
    )
