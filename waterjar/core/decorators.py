from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def owner_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not request.user.is_owner:
            messages.error(request, "Access denied. Owner privileges required.")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not request.user.is_staff_role:
            messages.error(request, "Access denied. Staff privileges required.")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper
