from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [

    # Home Route
    path('', views.HomeView.as_view(), name='home'),

    # Product Routes
    path('zenova.com/products/', views.ProductListView.as_view(), name='product_list'),
    path('zenova.com/products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('zenova.com/products/<int:product_id>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('zenova.com/products/<int:product_id>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('zenova.com/products/<int:product_id>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('zenova.com/products/list',views.ProductLListAdminView.as_view(),name= 'product_list_admin'),

    # Product Category Routes
    path('zenova.com/categories/', views.CategoryListView.as_view(), name='category_list'),
    path('zenova.com/categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('zenova.com/categories/<int:category_id>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('zenova.com/categories/<int:category_id>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('zenova.com/categories/<int:category_id>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Product Order Routes
    path("zenova.com/order/preview/", views.OrderPreviewView.as_view(), name="order_preview"),
    path("zenova.com/order/create", views.OrderCreateView.as_view(), name="order_create"),
    path('zenova.com/orders/',views.OrderListAdminView.as_view(), name='order_adminlist'),
    path("zenova.com/my-orders/",views.OrderListCustomerView.as_view(),name="order_list"),
    path("zenova.com/order/<int:order_id>/cancel/",views.OrderCancelView.as_view(),name="order_cancel"),

    # Cart Routes
    path('zenova.com/cart/', views.CartDetailView.as_view(), name='cart_detail'),
    path('zenova.com/cart/add/', views.CartAddItemView.as_view(), name='cart_add'),
    path('zenova.com/cart/update/', views.CartUpdateItemView.as_view(), name='cart_update'),
    path('zenova.com/cart/remove/', views.CartRemoveItemView.as_view(), name='cart_remove'),
    path('zenova.com/cart/clear/', views.CartClearView.as_view(), name='cart_clear'),

    # Product Review Routes
    path('zenova.com/products/<int:product_id>/reviews/', views.ProductReviewListView.as_view(), name='review_list'),
    path('zenova.com/products/<int:product_id>/reviews/create/', views.ProductReviewCreateView.as_view(), name='review_create'),
    path('zenova.com/products/<int:product_id>/reviews/update/', views.ProductReviewUpdateView.as_view(), name='review_update'),
    path('zenova.com/products/<int:product_id>/reviews/delete/', views.ProductReviewDeleteView.as_view(), name='review_delete'),

    # Cart Wishlist Routes
    path('zenova.com/wishlist/', views.WishlistListView.as_view(), name='wishlist'),
    path('zenova.com/wishlist/add/<int:product_id>/', views.WishlistAddView.as_view(), name='wishlist_add'),
    path('zenova.com/wishlist/remove/<int:product_id>/', views.WishlistRemoveView.as_view(), name='wishlist_remove'),
    path('zenova.com/wishlist/to/cart/<int:product_id>/', views.WishToCartView.as_view(), name='wishlist_cart'),

    # Product Coupon Routes
    path('zenova.com/coupons/', views.CouponListView.as_view(), name='coupon_list'),
    path('zenova.com/coupons/create/', views.CouponCreateView.as_view(), name='coupon_create'),
    path('zenova.com/coupons/<int:coupon_id>/update/', views.CouponUpdateView.as_view(), name='coupon_update'),
    path('zenova.com/coupons/<int:coupon_id>/delete/', views.CouponDeleteView.as_view(), name='coupon_delete'),
    path('zenova.com/coupons/<int:coupon_id>/apply/', views.CouponApplyView.as_view(), name='coupon_apply'),

    # Product Shipment Routes
    path('zenova.com/shipments/',views.ShipmentListView.as_view(),name='shipment_list'),
    path('zenova.com/shipments/<int:order_id>/', views.ShipmentDetailView.as_view(), name='shipment_detail'),
    path('zenova.com/shipments/<int:order_id>/create/', views.ShipmentCreateView.as_view(), name='shipment_create'),
    path('zenova.com/shipments/<int:order_id>/update-tracking/', views.ShipmentUpdateTrackingView.as_view(),  name='shipment_update_tracking'),
    path('zenova.com/shipments/<int:order_id>/mark-shipped/', views.ShipmentMarkShippedView.as_view(), name='shipment_mark_shipped'),
    path('zenova.com/shipments/<int:order_id>/mark-delivered/', views.ShipmentMarkDeliveredView.as_view(), name='shipment_mark_delivered'),

    # Product Search Routes
    path('zenova.com/products/search/', views.ProductSearchView.as_view(), name='product_search'),

    # Assign Coupon to User
    path('zenova.com/coupons/<int:coupon_id>/assign/', views.AssignCouponToUserView.as_view(), name='assign_coupon_to_user'),

    # Customer Routes for Coupon Management
    path('zenova.com/my-coupons/', views.CustomerCouponListView.as_view(), name='customer_coupon_list'),

    # Policy Terms
    path('terms-of-use/', TemplateView.as_view(template_name="policies/terms_of_use.html"), name="terms_of_use"),
    path('privacy-policy/', TemplateView.as_view(template_name="policies/privacy_policy.html"), name="privacy_policy"),
    path('payment-policy/', TemplateView.as_view(template_name="policies/payment_policy.html"), name="payment_policy"),
    path('warranty-service/', TemplateView.as_view(template_name="policies/warranty_service.html"), name="warranty_service"),



]






