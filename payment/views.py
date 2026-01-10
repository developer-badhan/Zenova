# payment/views.py
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.apps import apps
from django.contrib import messages
from . import services
from .models import Payment, PaymentMethod
from decorators import inject_authenticated_user, customer_required 
from django.utils.decorators import method_decorator


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


'''
class ZPayPaymentView(View):
    @customer_required
    @inject_authenticated_user
    def get(self, request, order_id, *args, **kwargs):
        Order = apps.get_model('shop', 'Order')
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect('cart_detail')
        return render(request, 'payment/zpay_payment.html', {'order': order})

    @customer_required
    @inject_authenticated_user
    def post(self, request, order_id, *args, **kwargs):
        # Simulate payment processing.
        Order = apps.get_model('shop', 'Order')
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect('cart_detail')

        # Find the latest payment record for this order / user
        payment = Payment.objects.filter(user=request.user, order_id=order.id).order_by('-created_at').first()
        if not payment:
            payment = services.create_payment_record(request.user, order, method=PaymentMethod.ZPAY.value, amount=order.total_amount)

        # Optionally inspect posted form fields (card details), but we won't store sensitive info.
        card_name = request.POST.get('card_name')
        card_number = request.POST.get('card_number')

        # Simulate gateway response: assume success
        payment, order = services.complete_payment(payment, gateway_txn_id=None, gateway_meta={'gateway': 'zpay', 'card_holder': card_name})

        # mark session flag so order_detail shows popup
        request.session['payment_success'] = True

        messages.success(request, "Payment successful.")
        return redirect(reverse('payment:order_detail', kwargs={'order_id': order.id}))
'''


# payment/views.py (add below existing view)
from .models import PaymentStatus
from .services import create_payment, process_zpay_payment


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

        payment = create_payment(user=request.user, order=order)

        return render(
            request,
            "payment/zpayment.html",
            {"order": order, "payment": payment},
        )

    @customer_required
    @inject_authenticated_user
    def post(self, request, order_id):
        Order = apps.get_model('shop', 'Order')
        order = Order.objects.get(id=order_id, user=request.user)
        payment = Payment.objects.get(order_id=order.id)

        success = process_zpay_payment(payment=payment, order=order)

        if success:
            messages.success(request, "Payment successful 🎉")
            return redirect("order_detail", order_id=order.id)

        messages.error(request, "Payment failed. Please try again.")
        return redirect("payment:zpay_payment", order_id=order.id)



class PaymentHistoryView(View):
    @customer_required
    @inject_authenticated_user
    def get(self, request):
        payments = Payment.objects.filter(user=request.user).order_by('-created_at')
        return render(request, "payment/history.html", {"payments": payments})
