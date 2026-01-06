from django.db import models
from django.conf import settings
from .coupon_model import Coupon

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    payment_status = models.CharField(max_length=50, default='pending')
    payment = models.OneToOneField('payment.Payment',on_delete=models.SET_NULL,null=True,blank=True,
        related_name='order_ref'
    )

    def __str__(self):
        return f"Order #{self.id} by {self.user}"
