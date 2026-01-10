from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.apps import apps
from django.contrib import messages
from payment.models import Payment, PaymentMethod
from decorators import inject_authenticated_user, customer_required 
from payment import services



# Payment Method Choose
class ChoosePaymentMethodView(View):
    @customer_required
    @inject_authenticated_user
    def get(self, request, order_id, *args, **kwargs):
        Order = apps.get_model('shop', 'Order')
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect('cart_detail')
        return render(request, 'payment/select_method.html', {'order': order})

    @customer_required
    @inject_authenticated_user
    def post(self, request, order_id, *args, **kwargs):
        method = int(request.POST.get('method', PaymentMethod.ZPAY.value))
        if method == PaymentMethod.ZPAY.value:
            return redirect(reverse('payment:zpay_payment', kwargs={'order_id': order_id}))
        messages.error(request, "Selected payment method not implemented.")
        return redirect(reverse('payment:choose_method', kwargs={'order_id': order_id}))


# Z-Payment View
# Z-Payment View
class ZPayPaymentView(View):
    @customer_required
    @inject_authenticated_user
    def get(self, request, order_id):
        Order = apps.get_model('shop', 'Order')
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect("cart_detail")

        if order.is_paid:
            messages.warning(request, "Order already paid.")
            return redirect("order_list")

        payment = services.create_payment(user=request.user, order=order)

        return render(request, "payment/zpayment.html", {
            "order": order,
            "payment": payment
        })

    @customer_required
    @inject_authenticated_user
    def post(self, request, order_id):
        Order = apps.get_model('shop', 'Order')
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect("cart_detail")

        if order.is_paid:
            messages.warning(request, "Order already paid.")
            return redirect("order_list")

        payment = services.create_payment(user=request.user, order=order)

        # 🔴 PASS request explicitly
        success = services.process_zpay_payment(
            payment=payment,
            order=order,
            request=request
        )

        if success:
            messages.success(request, "Payment successful 🎉")
            return redirect("order_list")

        messages.error(request, "Payment failed. Please try again.")
        return redirect("payment:zpay_payment", order_id=order.id)


# Payment History 
class PaymentHistoryView(View):
    @customer_required
    @inject_authenticated_user
    def get(self, request):
        payments = Payment.objects.filter(user=request.user).order_by('-created_at')
        return render(request, "payment/history.html", {"payments": payments})

