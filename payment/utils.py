
'''
# payment/utils.py
from django.shortcuts import reverse, redirect
from django.http import JsonResponse

def ajax_response(success=True, message="", data=None, status=200):
    return JsonResponse({'success': success, 'message': message, 'data': data or {}}, status=status)

def redirect_to_order(order_id):
    return redirect(reverse('payment:order_detail', kwargs={'order_id': order_id}))

'''

# payment/utils.py
import random
import time
from .models import generate_txn_id

def simulate_gateway_delay():
    time.sleep(2)  # fake network delay

def simulate_payment_result():
    """
    80% success, 20% failure
    """
    return random.choices(
        population=["success", "failure"],
        weights=[80, 20],
        k=1
    )[0]

def build_transaction_meta(order_id, method):
    return {
        "order_id": order_id,
        "method": method,
        "gateway": "Z-PAY-DUMMY",
    }
