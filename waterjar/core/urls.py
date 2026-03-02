from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ───────────────────────────────────────────────────────────────
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # ── Dashboard (auto-routes by role) ────────────────────────────────────
    path("dashboard/", views.dashboard, name="dashboard"),

    # ── Owner: Staff management ────────────────────────────────────────────
    path("staff/", views.staff_list, name="staff_list"),
    path("staff/add/", views.staff_create, name="staff_create"),
    path("staff/<int:pk>/edit/", views.staff_edit, name="staff_edit"),
    path("staff/<int:pk>/toggle/", views.staff_toggle_active, name="staff_toggle_active"),

    # ── Owner: View all customers ──────────────────────────────────────────
    path("owner/customers/", views.owner_customer_list, name="owner_customer_list"),

    # ── Owner: View all deliveries ─────────────────────────────────────────
    path("owner/deliveries/", views.owner_delivery_list, name="owner_delivery_list"),

    # ── Owner: Pending payments ────────────────────────────────────────────
    path("owner/pending/", views.pending_payments, name="pending_payments"),
    path("owner/mark-paid/<int:pk>/", views.mark_paid, name="mark_paid"),

    # ── Owner: Salary management ───────────────────────────────────────────
    path("salaries/", views.salary_list, name="salary_list"),
    path("salaries/add/", views.salary_create, name="salary_create"),
    path("salaries/<int:pk>/edit/", views.salary_edit, name="salary_edit"),

    # ── Staff: Customer management ─────────────────────────────────────────
    path("customers/", views.staff_customer_list, name="staff_customer_list"),
    path("customers/add/", views.customer_create, name="customer_create"),
    path("customers/<int:pk>/edit/", views.customer_edit, name="customer_edit"),

    # ── Staff: Delivery management ─────────────────────────────────────────
    path("deliveries/", views.staff_delivery_list, name="staff_delivery_list"),
    path("deliveries/add/", views.delivery_create, name="delivery_create"),
]