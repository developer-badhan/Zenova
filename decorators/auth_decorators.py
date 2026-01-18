from functools import wraps
from django.shortcuts import redirect
from django.urls import resolve
from constants.enums import Role
from django.contrib.auth import get_user_model



# Sign-in required decorator
def signin_required(view_func):
    @wraps(view_func)
    def wrapper(view_self, request, *args, **kwargs):
        if not hasattr(request, 'session') or not request.session.get('is_authenticated'):
            current_view_name = resolve(request.path_info).url_name
            if current_view_name != 'user_login':
                return redirect('user_login')
        return view_func(view_self, request, *args, **kwargs)
    return wrapper


# Customer role required decorator
def customer_required(view_func):
    @wraps(view_func)
    def wrapper(view_self, request, *args, **kwargs):
        if not request.session.get('is_authenticated') or request.session.get('user_role') != Role.ENDUSER_CUSTOMER:
            current_view_name = resolve(request.path_info).url_name
            if current_view_name != 'user_login':
                return redirect('user_login')
        return view_func(view_self, request, *args, **kwargs)
    return wrapper


# Staff role required decorator
def staff_required(view_func):
    @wraps(view_func)
    def wrapper(view_self, request, *args, **kwargs):
        if not request.session.get('is_authenticated') or request.session.get('user_role') != Role.ENDUSER_STAFF:
            current_view_name = resolve(request.path_info).url_name
            if current_view_name != 'user_login':
                return redirect('user_login')
        return view_func(view_self, request, *args, **kwargs)
    return wrapper


# Login required decorator
def login_admin_required(view_func):
    @wraps(view_func)
    def wrapper(view_self, request, *args, **kwargs):
        if not request.session.get('is_authenticated'):
            return redirect('admin_login')
        user_role = request.session.get('user_role')
        if user_role != Role.ADMIN:
            return redirect('user_login')
        return view_func(view_self, request, *args, **kwargs)
    return wrapper


# Inject authenticated user into request
def inject_authenticated_user(view_func):
    @wraps(view_func)
    def wrapper(view_self, request, *args, **kwargs):
        if not request.session.get('is_authenticated'):
            return redirect('user_login')
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user_model = get_user_model()
                request.user = user_model.objects.get(id=user_id)
            except user_model.DoesNotExist:
                return redirect('user_login')
        else:
            return redirect('user_login')
        return view_func(view_self, request, *args, **kwargs)
    return wrapper


# Inject authenticated admin user into request
def login_admin_required_with_user(view_func):
    @wraps(view_func)
    def wrapper(view_self, request, *args, **kwargs):
        if not request.session.get('is_authenticated'):
            return redirect('admin_login')
        user_role = request.session.get('user_role')
        if user_role != Role.ADMIN:
            return redirect('user_login')

        user_id = request.session.get('user_id')
        user_model = get_user_model()
        try:
            request.user = user_model.objects.get(id=user_id)
        except user_model.DoesNotExist:
            return redirect('user_login')
        return view_func(view_self, request, *args, **kwargs)
    return wrapper


# Combined decorator for class-based views with authentication
def staff_view_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'session') or not request.session.get('is_authenticated'):
            return redirect('user_login')
        if request.session.get('user_role') != Role.ENDUSER_STAFF:
            return redirect('user_login')
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user_model = get_user_model()
                request.user = user_model.objects.get(id=user_id)
            except user_model.DoesNotExist:
                return redirect('user_login')
        else:
            return redirect('user_login')
        return view_func(request, *args, **kwargs)
    return wrapper