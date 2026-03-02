from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


# ===========================================================================
# Custom User — supports Owner and Staff roles
# ===========================================================================
class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        STAFF = "staff", "Staff"

    role = models.CharField(
        max_length=10, choices=Role.choices, default=Role.STAFF
    )
    phone = models.CharField(max_length=15, blank=True)

    @property
    def is_owner(self):
        return self.role == self.Role.OWNER

    @property
    def is_staff_role(self):
        return self.role == self.Role.STAFF

    def str(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


# ===========================================================================
# Customer — regular (daily) or temporary (one-time)
# ===========================================================================
class Customer(models.Model):
    class Type(models.TextChoices):
        REGULAR = "regular", "Regular"
        TEMPORARY = "temporary", "Temporary"

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    type = models.CharField(
        max_length=10, choices=Type.choices, default=Type.REGULAR
    )
    jar_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price per jar for this customer",
    )
    security_deposit = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, blank=True
    )
    assigned_staff = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": User.Role.STAFF},
        related_name="customers",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def str(self):
        return f"{self.name} ({self.get_type_display()})"


# ===========================================================================
# Delivery — daily jar delivery record
# ===========================================================================
class Delivery(models.Model):
    class PaymentStatus(models.TextChoices):
        PAID = "paid", "Paid"
        PENDING = "pending", "Pending"

    class PaymentMode(models.TextChoices):
        CASH = "cash", "Cash"
        ONLINE = "online", "Online"

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="deliveries"
    )