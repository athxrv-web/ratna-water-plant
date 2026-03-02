from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import User, Customer, Delivery, Salary
from .forms import (
    StaffCreateForm,
    StaffEditForm,
    CustomerForm,
    DeliveryForm,
    SalaryForm,
)
from .decorators import owner_required, staff_required
from .utils import send_whatsapp_receipt


# ===========================================================================
# AUTHENTICATION
# ===========================================================================

def login_view(request):
    """Login page — redirects to dashboard if already logged in."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect("dashboard")
        messages.error(request, "Invalid username or password.")

    return render(request, "registration/login.html")


def logout_view(request):
    """Log out and redirect to login page."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")
# ===========================================================================
# STAFF — Customer Management
# ===========================================================================

@login_required
@staff_required
def staff_customer_list(request):
    q = request.GET.get("q", "").strip()
    customers = Customer.objects.filter(is_active=True).select_related(
        "assigned_staff"
    )
    if q:
        customers = customers.filter(
            Q(nameicontains=q) | Q(phoneicontains=q)
        )
    return render(
        request,
        "core/customer_list.html",
        {"customers": customers, "search_query": q, "is_owner_view": False},
    )


@login_required
@staff_required
def customer_create(request):
    form = CustomerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        customer = form.save(commit=False)
        # Auto-assign to current staff if not set
        if not customer.assigned_staff:
            customer.assigned_staff = request.user
        customer.save()
        messages.success(request, f"Customer '{customer.name}' added successfully.")
        return redirect("staff_customer_list")
    return render(request, "core/form_page.html", {"form": form, "title": "Add Customer"})


@login_required
@staff_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Customer '{customer.name}' updated.")
        return redirect("staff_customer_list")
    return render(
        request,
        "core/form_page.html",
        {"form": form, "title": f"Edit Customer — {customer.name}"},
    )


# ===========================================================================
# STAFF — Delivery Management
# ===========================================================================

@login_required
@staff_required
def delivery_create(request):
    form = DeliveryForm(request.POST or None, staff_user=request.user)
    if request.method == "POST" and form.is_valid():
        delivery = form.save(commit=False)
        delivery.staff = request.user
        delivery.save()

        # Send WhatsApp receipt (placeholder)
        send_whatsapp_receipt(delivery.customer, delivery.amount)

        messages.success(
            request,
            f"Delivery recorded: {delivery.jar_count} jars → "
            f"{delivery.customer.name} (₹{delivery.amount})",
        )
        return redirect("staff_delivery_list")
    return render(request, "core/delivery_form.html", {"form": form})


@login_required
@staff_required
def staff_delivery_list(request):
    deliveries = (
        Delivery.objects.filter(staff=request.user)
        .select_related("customer")
        .order_by("-date", "-created_at")[:50]
    )
    return render(
        request,
        "core/delivery_list.html",
        {"deliveries": deliveries, "is_owner_view": False},
    )