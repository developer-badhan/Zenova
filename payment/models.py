# payment/models.py
import uuid
from enum import IntEnum
from django.db import models
from django.conf import settings

class PaymentMethod(IntEnum):
    ZPAY = 1
    COD = 2

    @classmethod
    def choices(cls):
        return [(m.value, m.name) for m in cls]

class PaymentStatus(IntEnum):
    INITIATED = 1
    SUCCESS = 2
    FAILED = 3

    @classmethod
    def choices(cls):
        return [(s.value, s.name) for s in cls]

def generate_txn_id(prefix="ZPAY"):
    return f"{prefix.upper()}-{uuid.uuid4()}"

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    # Keep order FK optional (we will link Order.payment -> Payment as OneToOne), but store order_id for ease.
    order_id = models.PositiveIntegerField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.IntegerField(choices=PaymentMethod.choices(), default=PaymentMethod.ZPAY.value)
    status = models.IntegerField(choices=PaymentStatus.choices(), default=PaymentStatus.INITIATED.value)
    transaction_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    meta = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_success(self, txn_id=None, meta=None):
        self.status = PaymentStatus.SUCCESS.value
        if txn_id:
            self.transaction_id = txn_id
        if meta is not None:
            self.meta = meta
        self.save(update_fields=['status', 'transaction_id', 'meta', 'updated_at'])

    def mark_failed(self, txn_id=None, meta=None):
        self.status = PaymentStatus.FAILED.value
        if txn_id:
            self.transaction_id = txn_id
        if meta is not None:
            self.meta = meta
        self.save(update_fields=['status', 'transaction_id', 'meta', 'updated_at'])

    def __str__(self):
        status_display = dict(PaymentStatus.choices()).get(self.status, str(self.status))
        return f"Payment #{self.id} - Order {self.order_id} - {status_display}"
