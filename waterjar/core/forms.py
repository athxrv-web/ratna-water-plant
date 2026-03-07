from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Customer, Delivery, Salary

INPUT = (
    "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
)


def _tw(form):
    for field in form.fields.values():
        w = field.widget
        if isinstance(w, forms.CheckboxInput):
            w.attrs["class"] = "h-4 w-4 rounded border-gray-300 text-blue-600"
        elif isinstance(w, forms.Textarea):
            w.attrs.update({"class": INPUT + " resize-none", "rows": 3})
        elif isinstance(w, forms.Select):
            w.attrs["class"] = INPUT
        else:
            w.attrs["class"] = INPUT


class StaffCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "phone", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _tw(self)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STAFF
        if commit:
            user.save()
        return user


class StaffEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _tw(self)


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("name", "phone", "address", "type", "jar_price", "security_deposit", "assigned_staff", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _tw(self)
        self.fields["assigned_staff"].queryset = User.objects.filter(role=User.Role.STAFF, is_active=True)
        self.fields["assigned_staff"].required = False
        self.fields["security_deposit"].required = False


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ("customer", "date", "jar_count", "payment_status", "payment_mode")

    def __init__(self, *args, staff_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        _tw(self)
        self.fields["date"].widget = forms.DateInput(attrs={"class": INPUT, "type": "date"})
        self.fields["customer"].queryset = Customer.objects.filter(is_active=True)


class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = ("staff", "month", "salary_amount", "status")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _tw(self)
        self.fields["staff"].queryset = User.objects.filter(role=User.Role.STAFF, is_active=True)
        self.fields["month"].widget = forms.DateInput(attrs={"class": INPUT, "type": "date"})
