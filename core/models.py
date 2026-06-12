from datetime import date

from django.contrib.auth.models import User
from django.db import models


REGION_CHOICES = [
    ('North India', 'North India'),
    ('South India', 'South India'),
    ('East India', 'East India'),
    ('West India', 'West India'),
]


class UserRole(models.Model):
    """A role like CEM, TSE, etc. (the 'User Role' dropdown on Add Employee)."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Extra info attached to a Django login user."""
    USER_TYPE_CHOICES = [
        ('Super Admin', 'Super Admin'),
        ('Admin', 'Admin'),
        ('MD', 'MD'),
        ('Employee', 'Employee'),
        ('Partner', 'Partner'),
        ('Distributer', 'Distributer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='Employee')
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True)
    region = models.CharField(max_length=20, choices=REGION_CHOICES, blank=True)
    contact_no = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Series(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Series'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    series = models.ForeignKey(Series, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Case Locked', 'Case Locked'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    ticket_no = models.CharField(max_length=30, unique=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='complaints')
    customer_name = models.CharField(max_length=200)
    customer_mobile = models.CharField(max_length=15)
    spoc = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='complaints', verbose_name='SPOC')
    distributor_partner = models.CharField(max_length=200, blank=True)
    distributor_mobile = models.CharField(max_length=15, blank=True)
    region = models.CharField(max_length=20, choices=REGION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    description = models.TextField(blank=True)

    registration_date = models.DateField(default=date.today)
    closed_date = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-set closed_date when complaint is resolved/closed
        if self.status in ('Resolved', 'Closed') and self.closed_date is None:
            self.closed_date = date.today()
        if self.status not in ('Resolved', 'Closed'):
            self.closed_date = None
        super().save(*args, **kwargs)
        # Ticket number needs the database id, so set it after the first save
        if not self.ticket_no:
            self.ticket_no = f"#TicketNo-{self.pk + 7000} - {self.registration_date.strftime('%d%m%Y')}"
            super().save(update_fields=['ticket_no'])

    @property
    def days_open(self):
        """How many days the complaint has been (or was) open — the client's key metric."""
        end = self.closed_date or date.today()
        return (end - self.registration_date).days

    @property
    def days_color(self):
        """green = fast, yellow = warning, red = too slow."""
        d = self.days_open
        if d <= 2:
            return 'success'   # green
        if d <= 7:
            return 'warning'   # yellow
        return 'danger'        # red

    def __str__(self):
        return self.ticket_no


class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question
