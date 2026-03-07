from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        STAFF = "staff", "Staff"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STAFF)
    phone = models.CharField(max_length=15, blank=True)

    @property
    def is_owner(self):
        return self.role == self.Role.OWNER

    @property
    def is_staff_role(self):
        return self.role == self.Role.STAFF

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class Customer(models.Model):
    class Type(models.TextChoices):
        REGULAR = "regular", "Regular"
        TEMPORARY = "temporary", "Temporary"

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.REGULAR)
    jar_price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    security_deposit = models.DecimalField(max_digits=8, decimal_places=2, default=0, blank=True)
    assigned_staff = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={"role": User.Role.STAFF}, related_name="customers",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Delivery(models.Model):
    class PaymentStatus(models.TextChoices):
        PAID = "paid", "Paid"
        PENDING = "pending", "Pending"

    class PaymentMode(models.TextChoices):
        CASH = "cash", "Cash"
        ONLINE = "online", "Online"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="deliveries")
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="deliveries")
    date = models.DateField()
    jar_count = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    payment_status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    payment_mode = models.CharField(max_length=10, choices=PaymentMode.choices, default=PaymentMode.CASH)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name_plural = "deliveries"

    def save(self, *args, **kwargs):
        self.amount = self.jar_count * self.customer.jar_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.name} - {self.jar_count} jars on {self.date}"


class Salary(models.Model):
    class Status(models.TextChoices):
        PAID = "paid", "Paid"
        UNPAID = "unpaid", "Unpaid"

    staff = models.ForeignKey(
        User, on_delete=models.CASCADE,
        limit_choices_to={"role": User.Role.STAFF}, related_name="salaries",
    )
    month = models.DateField(help_text="First day of the month")
    salary_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UNPAID)

    class Meta:
        ordering = ["-month"]
        verbose_name_plural = "salaries"
        unique_together = ["staff", "month"]

    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.month.strftime('%B %Y')}"
