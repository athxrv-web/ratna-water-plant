from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import User, Customer, Delivery, Salary
from .forms import StaffCreateForm, StaffEditForm, CustomerForm, DeliveryForm, SalaryForm
from .decorators import owner_required, staff_required
from .utils import send_whatsapp_receipt


# === AUTH ===

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username", "").strip(), password=request.POST.get("password", ""))
        if user:
            login(request, user)
            messages.success(request, f"Welcome, {user.get_full_name() or user.username}!")
            return redirect("dashboard")
        messages.error(request, "Invalid username or password.")
    return render(request, "registration/login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


# === DASHBOARD ===

@login_required
def dashboard(request):
    if request.user.is_owner:
        return _owner_dashboard(request)
    return _staff_dashboard(request)


def _owner_dashboard(request):
    today = timezone.localdate()
    first = today.replace(day=1)
    td = Delivery.objects.filter(date=today)
    md = Delivery.objects.filter(date__gte=first, date__lte=today)
    pq = Delivery.objects.filter(payment_status="pending")
    stats = {
        "total_customers": Customer.objects.count(),
        "active_customers": Customer.objects.filter(is_active=True).count(),
        "today_deliveries": td.count(),
        "today_revenue": td.filter(payment_status="paid").aggregate(t=Sum("amount"))["t"] or 0,
        "monthly_revenue": md.filter(payment_status="paid").aggregate(t=Sum("amount"))["t"] or 0,
        "pending_payments": pq.aggregate(t=Sum("amount"))["t"] or 0,
        "total_staff": User.objects.filter(role=User.Role.STAFF, is_active=True).count(),
    }
    recent = Delivery.objects.select_related("customer", "staff")[:10]
    return render(request, "core/owner_dashboard.html", {"stats": stats, "recent_deliveries": recent})


def _staff_dashboard(request):
    today = timezone.localdate()
    my = Delivery.objects.filter(staff=request.user, date=today).select_related("customer")
    stats = {
        "today_deliveries": my.count(),
        "today_jars": my.aggregate(t=Sum("jar_count"))["t"] or 0,
        "today_revenue": my.filter(payment_status="paid").aggregate(t=Sum("amount"))["t"] or 0,
        "my_customers": Customer.objects.filter(assigned_staff=request.user, is_active=True).count(),
        "pending_collections": Delivery.objects.filter(staff=request.user, payment_status="pending").aggregate(t=Sum("amount"))["t"] or 0,
    }
    return render(request, "core/staff_dashboard.html", {"stats": stats, "today_deliveries": my})


# === OWNER: STAFF ===

@login_required
@owner_required
def staff_list(request):
    return render(request, "core/staff_list.html", {
        "staff_members": User.objects.filter(role=User.Role.STAFF).order_by("-is_active", "first_name")
    })


@login_required
@owner_required
def staff_create(request):
    form = StaffCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Staff created.")
        return redirect("staff_list")
    return render(request, "core/staff_form.html", {"form": form, "title": "Add Staff Member"})


@login_required
@owner_required
def staff_edit(request, pk):
    staff = get_object_or_404(User, pk=pk, role=User.Role.STAFF)
    form = StaffEditForm(request.POST or None, instance=staff)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Staff updated.")
        return redirect("staff_list")
    return render(request, "core/staff_form.html", {"form": form, "title": f"Edit — {staff.get_full_name()}"})


@login_required
@owner_required
def staff_toggle_active(request, pk):
    staff = get_object_or_404(User, pk=pk, role=User.Role.STAFF)
    staff.is_active = not staff.is_active
    staff.save(update_fields=["is_active"])
    messages.success(request, f"{staff.get_full_name()} {'activated' if staff.is_active else 'deactivated'}.")
    return redirect("staff_list")


# === OWNER: CUSTOMERS / DELIVERIES / PAYMENTS / SALARY ===

@login_required
@owner_required
def owner_customer_list(request):
    q = request.GET.get("q", "").strip()
    qs = Customer.objects.select_related("assigned_staff")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(phone__icontains=q))
    return render(request, "core/customer_list.html", {"customers": qs, "search_query": q, "is_owner_view": True})


@login_required
@owner_required
def owner_delivery_list(request):
    df = request.GET.get("date", "")
    qs = Delivery.objects.select_related("customer", "staff")
    if df:
        qs = qs.filter(date=df)
    else:
        qs = qs[:50]
    return render(request, "core/delivery_list.html", {"deliveries": qs, "date_filter": df, "is_owner_view": True})


@login_required
@owner_required
def pending_payments(request):
    qs = Delivery.objects.filter(payment_status="pending").select_related("customer", "staff").order_by("-date")
    total = qs.aggregate(t=Sum("amount"))["t"] or 0
    return render(request, "core/pending_payments.html", {"deliveries": qs, "total_pending": total})


@login_required
@owner_required
def mark_paid(request, pk):
    d = get_object_or_404(Delivery, pk=pk)
    d.payment_status = Delivery.PaymentStatus.PAID
    d.save(update_fields=["payment_status"])
    messages.success(request, f"Rs{d.amount} from {d.customer.name} marked paid.")
    return redirect(request.META.get("HTTP_REFERER", "pending_payments"))


@login_required
@owner_required
def salary_list(request):
    return render(request, "core/salary_list.html", {"salaries": Salary.objects.select_related("staff")})


@login_required
@owner_required
def salary_create(request):
    form = SalaryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Salary record added.")
        return redirect("salary_list")
    return render(request, "core/salary_form.html", {"form": form, "title": "Add Salary Record"})


@login_required
@owner_required
def salary_edit(request, pk):
    salary = get_object_or_404(Salary, pk=pk)
    form = SalaryForm(request.POST or None, instance=salary)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Salary updated.")
        return redirect("salary_list")
    return render(request, "core/salary_form.html", {"form": form, "title": "Edit Salary Record"})


# === STAFF: CUSTOMERS ===

@login_required
@staff_required
def staff_customer_list(request):
    q = request.GET.get("q", "").strip()
    qs = Customer.objects.filter(is_active=True).select_related("assigned_staff")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(phone__icontains=q))
    return render(request, "core/customer_list.html", {"customers": qs, "search_query": q, "is_owner_view": False})


@login_required
@staff_required
def customer_create(request):
    form = CustomerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        c = form.save(commit=False)
        if not c.assigned_staff:
            c.assigned_staff = request.user
        c.save()
        messages.success(request, f"Customer '{c.name}' added.")
        return redirect("staff_customer_list")
    return render(request, "core/customer_form.html", {"form": form, "title": "Add Customer"})


@login_required
@staff_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Customer '{customer.name}' updated.")
        return redirect("staff_customer_list")
    return render(request, "core/customer_form.html", {"form": form, "title": f"Edit — {customer.name}"})


# === STAFF: DELIVERIES ===

@login_required
@staff_required
def delivery_create(request):
    form = DeliveryForm(request.POST or None, staff_user=request.user)
    if request.method == "POST" and form.is_valid():
        d = form.save(commit=False)
        d.staff = request.user
        d.save()
        result = send_whatsapp_receipt(d.customer, d)
        if result.get("status") == "sent":
            messages.info(request, f"WhatsApp receipt sent to {d.customer.name}.")
        messages.success(request, f"Delivery: {d.jar_count} jars to {d.customer.name} (Rs{d.amount})")
        return redirect("staff_delivery_list")
    return render(request, "core/delivery_form.html", {"form": form})


@login_required
@staff_required
def staff_delivery_list(request):
    qs = Delivery.objects.filter(staff=request.user).select_related("customer").order_by("-date", "-created_at")[:50]
    return render(request, "core/delivery_list.html", {"deliveries": qs, "is_owner_view": False})
