from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Customer, Delivery, Salary


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "get_full_name", "role", "phone", "is_active")
    list_filter = ("role", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (("Extra Info", {"fields": ("role", "phone")}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (("Extra Info", {"fields": ("role", "phone", "first_name", "last_name")}),)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "type", "jar_price", "assigned_staff", "is_active")
    list_filter = ("type", "is_active", "assigned_staff")
    search_fields = ("name", "phone")


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("customer", "staff", "date", "jar_count", "amount", "payment_status")
    list_filter = ("date", "payment_status", "staff")
    date_hierarchy = "date"


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ("staff", "month", "salary_amount", "status")
    list_filter = ("status", "staff")
