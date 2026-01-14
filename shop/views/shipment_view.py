from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from constants.enums import Role
from shop.services import shipment_service
from shop.models import Shipment
from decorators import signin_required,staff_required,customer_required,login_admin_required



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


# Staff shipment details
class StaffShipmentListView(View):
    @signin_required
    @staff_required
    def get(self,request):
        shipments = shipment_service.get_required_data()
        return render(request,'shipment/staff_shipment.html',{'shipments':shipments})



'''
class StaffMarkShipmentShippedView(View):
    @staff_required
    def post(self, request, shipment_id):
        try:
            shipment = Shipment.objects.get(id=shipment_id)

            shipment_service.mark_shipment_as_shipped(
                shipment=shipment,
                staff_user=request.user
            )

            messages.success(request, "Shipment marked as shipped.")

        except Exception as e:
            messages.error(request, str(e))

        return redirect("staff_shipments")


# ----------------------------------
# Mark shipment as delivered
# ----------------------------------
class StaffMarkShipmentDeliveredView(View):
    @staff_required
    def post(self, request, shipment_id):
        try:
            shipment = Shipment.objects.get(id=shipment_id)

            shipment_service.mark_shipment_as_delivered(
                shipment=shipment,
                staff_user=request.user
            )

            messages.success(request, "Shipment marked as delivered.")

        except Exception as e:
            messages.error(request, str(e))

        return redirect("staff_shipments")

'''





# class ShipmentMarkShippedView(View):
#     @signin_required
#     @staff_required
#     def post(self, request, shipment_id):
#         shipment = Shipment.objects.get(id=shipment_id)

#         shipment_service.mark_shipment_shipped(
#             shipment=shipment,
#             staff_user=request.user
#         )
#         return redirect("staff_shipments")



# class ShipmentMarkDeliveredView(View):
#     @signin_required
#     @staff_required
#     def post(self, request, shipment_id):
#         shipment = Shipment.objects.get(id=shipment_id)

#         shipment_service.mark_shipment_delivered(
#             shipment=shipment,
#             staff_user=request.user
#         )
#         return redirect("staff_shipments")


# Shipment Details for customer
class ShipmentDetailView(View):
    @signin_required
    @customer_required
    def get(self,request):
        shipment = shipment_service.get_shipment()
        return render(request,'shipment/detail.html',{'shipment':shipment})

 

