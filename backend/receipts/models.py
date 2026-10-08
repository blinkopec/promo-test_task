from django.db import models
from django.contrib.auth.models import User

class Receipt(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'На проверке'),
        (STATUS_ACCEPTED, 'Принят'),
        (STATUS_REJECTED, 'Отклонён'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='receipts',
    )

    fn = models.CharField('ФН', max_length=16)
    fd = models.CharField('ФД', max_length=10)
    fp = models.CharField('ФП', max_length=10)

    purchase_datetime = models.DateTimeField('Дата и время покупки')

    amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2)

    status = models.CharField(
        'Статус',
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    rejection_reason = models.TextField('Причина отказа', blank=True)

    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)

    class Meta:
        ordering = ['-purchase_datetime', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['fn', 'fd', 'fp'],
                name='unique_receipt_identity',
            )
        ]

    def __str__(self):
        return f'{self.fn} / {self.fd} / {self.fp}'