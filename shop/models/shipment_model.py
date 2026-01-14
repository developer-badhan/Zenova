from django.db import models
from django.conf import settings
from shop.models.order_model import Order
from enum import IntEnum


class ShipmentStatus(IntEnum):
    PENDING_ASSIGNMENT = 1
    ASSIGNED = 2
    SHIPPED = 3
    DELIVERED = 4
    FAILED = 5

    @classmethod
    def choices(cls):
        return [(s.value, s.name.replace("_", " ").title()) for s in cls]


class Shipment(models.Model):
    order = models.OneToOneField(Order,on_delete=models.CASCADE,related_name="shipment")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="shipments")
    address_snapshot = models.TextField()
    assigned_staff = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,
    related_name="staff_shipments")
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    carrier = models.CharField(max_length=100, null=True, blank=True)
    status = models.IntegerField(
        choices=ShipmentStatus.choices(),
        default=ShipmentStatus.PENDING_ASSIGNMENT
    )
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shipments"

    def __str__(self):
        return f"Shipment #{self.id} | Order #{self.order.id}"
