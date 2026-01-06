from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from shop.services import shipment_service
from shop.models import Order
from decorators import signin_required,staff_required,customer_required,login_admin_required




class ShipmentListView(View):
    @login_admin_required
    def get(self,request):
        try:
            shipment = shipment_service.get_all_shipment()
            return render(request,'shipment/shipment_list.html',{'shipment':shipment})
        except Exception as e:
            print(f"Shipment List was not found. Error :{e}")
            return redirect('admin_dahboard')




class ShipmentDetailView(View):
    @signin_required
    @customer_required
    def get(self, request, order_id):
        try:
            shipment = shipment_service.get_shipment_by_order(order_id)
            if shipment:
                return render(request, 'shipment/shipment_detail.html', {'shipment': shipment})
            messages.warning(request, "No shipment found for this order.")
            return redirect('order_detail', order_id=order_id)
        except Exception as e:
            print(f"[ShipmentDetailView] Error: {e}")
            messages.error(request, "Failed to load shipment details.")
            return redirect('order_list')


class ShipmentCreateView(View):
    @login_admin_required
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            return render(request, 'shipment/shipment_create.html', {'order': order})
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect('order_list')

    @login_admin_required
    def post(self, request, order_id):
        address = request.POST.get('address')
        tracking_number = request.POST.get('tracking_number', '')
        carrier = request.POST.get('carrier', '')

        try:
            shipment = shipment_service.create_shipment(
                order_id=order_id,
                address=address,
                tracking_number=tracking_number,
                carrier=carrier
            )
            if shipment:
                messages.success(request, "Shipment created successfully.")
            else:
                messages.error(request, "Failed to create shipment.")
        except Exception as e:
            print(f"[ShipmentCreateView] Error: {e}")
            messages.error(request, "An error occurred while creating the shipment.")

        return redirect('shipment_detail', order_id=order_id)

class ShipmentUpdateTrackingView(View):
    def post(self, request, order_id):
        tracking_number = request.POST.get('tracking_number')
        carrier = request.POST.get('carrier')

        try:
            shipment = shipment_service.update_tracking(order_id, tracking_number, carrier)
            if shipment:
                messages.success(request, "Tracking information updated.")
            else:
                messages.error(request, "Failed to update tracking information.")
        except Exception as e:
            print(f"[ShipmentUpdateTrackingView] Error: {e}")
            messages.error(request, "An error occurred while updating tracking.")

        return redirect('shipment_detail', order_id=order_id)

class ShipmentMarkShippedView(View):
    @signin_required
    @staff_required
    def post(self, request, order_id):
        try:
            shipment = shipment_service.mark_as_shipped(order_id)
            if shipment:
                messages.success(request, "Shipment marked as shipped.")
            else:
                messages.error(request, "Failed to mark shipment as shipped.")
        except Exception as e:
            print(f"[ShipmentMarkShippedView] Error: {e}")
            messages.error(request, "An error occurred while marking as shipped.")

        return redirect('shipment_detail', order_id=order_id)


class ShipmentMarkDeliveredView(View):
    @signin_required
    @staff_required
    def post(self, request, order_id):
        try:
            shipment = shipment_service.mark_as_delivered(order_id)
            if shipment:
                messages.success(request, "Shipment marked as delivered.")
            else:
                messages.error(request, "Failed to mark shipment as delivered.")
        except Exception as e:
            print(f"[ShipmentMarkDeliveredView] Error: {e}")
            messages.error(request, "An error occurred while marking as delivered.")

        return redirect('shipment_detail', order_id=order_id)
