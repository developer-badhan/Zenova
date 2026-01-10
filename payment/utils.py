import random
import time
from .models import generate_txn_id


# Network Buffer
def simulate_gateway_delay():
    time.sleep(2)  


# Payment  Succession Result
def simulate_payment_result():
    return "success"


# Additional Details
def build_transaction_meta(order_id, method):
    return {
        "order_id": order_id,
        "method": method,
        "gateway": "Z-PAY-DUMMY",
    }
