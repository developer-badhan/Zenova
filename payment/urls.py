# payment/urls.py
from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('order/<int:order_id>/choose-method/', views.ChoosePaymentMethodView.as_view(), name='choose_method'),
    path('order/<int:order_id>/zpay/', views.ZPayPaymentView.as_view(), name='zpay_payment'),
    path('history/', views.PaymentHistoryView.as_view(), name='payment_history'),
]


