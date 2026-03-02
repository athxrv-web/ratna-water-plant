from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Customer, Delivery, Salary


# ===========================================================================
# Tailwind CSS classes for form widgets
# ===========================================================================
INPUT_CSS = (
    "w-full px-3 py-2 border border-slate-300 rounded-lg text-sm "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 "
    "bg-white"
)
SELECT_CSS = INPUT_CSS
TEXTAREA_CSS = INPUT_CSS + " resize-none"
CHECKBOX_CSS = "h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"


def _apply_tailwind(form_instance):
    """Apply Tailwind classes to every field in a form."""
    for name, field in form_instance.fields.items():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs["class"] = CHECKBOX_CSS
        elif isinstance(widget, forms.Textarea):
            widget.attrs["class"] = TEXTAREA_CSS
            widget.attrs.setdefault("rows", 3)
        elif isinstance(widget, forms.Select):
            widget.attrs["class"] = SELECT_CSS
        else:
            widget.attrs["class"] = INPUT_CSS


class StaffCreateForm(UserCreationForm):
    """Create a new staff user account."""

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "phone",
            "password1",
            "password2",
        )

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)
        _apply_tailwind(self)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STAFF
        if commit:
            user.save()
        return user


class StaffEditForm(forms.ModelForm):
    """Edit existing staff details (no password change here)."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone", "is_active")

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)
        _apply_tailwind(self)

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = (
            "name",
            "phone",
            "address",
            "type",
            "jar_price",
            "security_deposit",
            "assigned_staff",
            "is_active",
        )

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)
        _apply_tailwind(self)
        # Only show active staff in the dropdown
        self.fields["assigned_staff"].queryset = User.objects.filter(
            role=User.Role.STAFF, is_active=True
        )
        self.fields["assigned_staff"].required = False
        self.fields["security_deposit"].required = False

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = (
            "customer",
            "date",
            "jar_count",
            "payment_status",
            "payment_mode",
        )

    def init(self, *args, staff_user=None, **kwargs):
        super().init(*args, **kwargs)
        _apply_tailwind(self)
        # Use HTML5 date picker
        self.fields["date"].widget = forms.DateInput(
            attrs={"class": INPUT_CSS, "type": "date"}
        )
        # Only show active customers
        self.fields["customer"].queryset = Customer.objects.filter(is_active=True)

class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = ("staff", "month", "salary_amount", "status")

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)
        _apply_tailwind(self)
        # Only active staff
        self.fields["staff"].queryset = User.objects.filter(
            role=User.Role.STAFF, is_active=True
        )
        # Date picker for month selection
        self.fields["month"].widget = forms.DateInput(
            attrs={"class": INPUT_CSS, "type": "date"}
        )
        self.fields["month"].help_text = "Pick the 1st day of the month"