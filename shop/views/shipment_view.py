from django.views import View
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from constants.enums import Role
from shop.services import shipment_service
from shop.models import Shipment
from decorators import signin_required,staff_view_required,customer_required,login_admin_required
from django.utils.decorators import method_decorator



# Shipment Management By Admin
class AdminShipmentListView(View):
    @login_admin_required
    def get(self, request):
        shipments = Shipment.objects.select_related("order", "assigned_staff", "customer")
        staff_users = shipment_service.get_all_staff_users()
        context ={
            "shipments": shipments,
            "staff_users": staff_users,
            }
        return render(request,"shipment/admin_list.html",context)


# Shipment Assignment To Staff
class ShipmentAssignStaffView(View):
    @login_admin_required
    def post(self, request, shipment_id):
        staff_id = request.POST.get("staff_id")
        try:
            shipment = Shipment.objects.get(id=shipment_id)
            staff_user = shipment_service.get_all_staff_users().get(id=staff_id)
            shipment_service.assign_staff_to_shipment(
                shipment=shipment,
                staff_user=staff_user
            )
            messages.success(request,f"Shipment assigned to {staff_user.email}")
        except Exception as e:
            messages.error(request, str(e))
        return redirect("shipment_admin_list")


# Staff shipment list view
@method_decorator(staff_view_required, name='dispatch')
class StaffShipmentListView(View):
    def get(self, request):
        shipments = shipment_service.get_required_data()
        return render(request, 'shipment/staff_shipment.html', {'shipments': shipments})


# Shipment Shipped View
@method_decorator(staff_view_required, name='dispatch')
class StaffMarkShipmentShippedView(View):
    def get(self, request, shipment_id):
        shipment = get_object_or_404(Shipment, id=shipment_id)
        return render(request, 'shipment/staff_mark_shipped.html', {'shipment': shipment})

    def post(self, request, shipment_id):
        try:
            shipment = get_object_or_404(Shipment, id=shipment_id)
            print(f"DEBUG: Shipment {shipment_id} current status: {shipment.status}")
            print(f"DEBUG: Assigned staff: {shipment.assigned_staff}")
            print(f"DEBUG: Current user: {request.user}")
            print(f"DEBUG: User is authenticated: {request.user.is_authenticated}")
            shipment_service.mark_shipment_as_shipped(
                shipment=shipment,
                staff_user=request.user
            )
            shipment.refresh_from_db()
            print(f"DEBUG: Shipment {shipment_id} new status: {shipment.status}")
            messages.success(request, "Shipment marked as shipped successfully.")
        except PermissionError as e:
            messages.error(request, f"Permission denied: {str(e)}")
            print(f"ERROR: PermissionError - {str(e)}")
        except ValueError as e:
            messages.error(request, f"Invalid operation: {str(e)}")
            print(f"ERROR: ValueError - {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            print(f"ERROR: Exception - {str(e)}")
        return redirect("staff_shipments")


# Mark shipment as delivered
@method_decorator(staff_view_required, name='dispatch')
class StaffMarkShipmentDeliveredView(View):
    def get(self, request, shipment_id):
        shipment = get_object_or_404(Shipment, id=shipment_id)
        return render(request, "shipment/staff_mark_delivered.html", {'shipment': shipment})
    
    def post(self, request, shipment_id):
        try:
            shipment = get_object_or_404(Shipment, id=shipment_id) 
            print(f"DEBUG: Shipment {shipment_id} current status: {shipment.status}")
            print(f"DEBUG: Assigned staff: {shipment.assigned_staff}")
            print(f"DEBUG: Current user: {request.user}")
            print(f"DEBUG: User is authenticated: {request.user.is_authenticated}")
            shipment_service.mark_shipment_as_delivered(
                shipment=shipment,
                staff_user=request.user
            )
            shipment.refresh_from_db()
            print(f"DEBUG: Shipment {shipment_id} new status: {shipment.status}")
            messages.success(request, "Shipment marked as delivered successfully.")
        except PermissionError as e:
            messages.error(request, f"Permission denied: {str(e)}")
            print(f"ERROR: PermissionError - {str(e)}")
        except ValueError as e:
            messages.error(request, f"Invalid operation: {str(e)}")
            print(f"ERROR: ValueError - {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            print(f"ERROR: Exception - {str(e)}")
        return redirect("staff_shipments")


# Shipment Details for customer
class ShipmentDetailView(View):
    @signin_required
    @customer_required
    def get(self,request):
        shipment = shipment_service.get_shipment()
        return render(request,'shipment/detail.html',{'shipment':shipment})

 

