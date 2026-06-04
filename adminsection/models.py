from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone


# Create your models here.
class Store(models.Model):
    StoreID = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    StoreName = models.CharField(max_length=100)
    Address = models.TextField()
    City = models.CharField(max_length=50)
    State = models.CharField(max_length=50)
    Pincode = models.CharField(max_length=10)
    Phone = models.CharField(max_length=15)
    CreatedAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.StoreName

class User(AbstractUser):

    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employee'),
        ('CUSTOMER', 'Customer'),
    )

    Role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    Store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username

class Employee(models.Model):
    User = models.OneToOneField(User, on_delete=models.CASCADE)
    EmployeeID = models.CharField(max_length=20, unique=True)
    JoiningDate = models.DateField()
    Salary = models.DecimalField(max_digits=10, decimal_places=2)
    Store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True)
    IsActive = models.BooleanField(default=True)
    Note = models.TextField(blank=True)

    def __str__(self):
        return self.User.username

class Customer(models.Model):
    """
    Customer identified by phone number (unique, but NOT the DB primary key).
    Keeping the default auto integer PK preserves existing Invoice FK references.
    """
    PhoneID = models.UUIDField(primary_key=True, default=uuid.uuid4)
    PhoneNumber = models.CharField(max_length=15, unique=True) 
    Name = models.CharField(max_length=150)
    Note = models.TextField(blank=True)
    CreateDate = models.DateTimeField(auto_now_add=True)
    UpdateDate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.Name} ({self.PhoneNumber})"

 
    @property
    def total_visits(self):
        return self.visits.count()
 
    @property
    def return_visits(self):
        """Visits after the very first one."""
        return max(self.visits.count() - 1, 0)
 
    @property
    def retention_rate(self):
        """
        Simple retention rate:
            (return visits / total visits) × 100
        Returns 0 for first-time customers.
        """
        total = self.total_visits
        if total <= 1:
            return 0.0
        return round((self.return_visits / total) * 100, 1)
 
    @property
    def last_visit(self):
        visit = self.visits.order_by('-VisitDate').first()
        return visit.VisitDate if visit else None
 
    @property
    def total_spent(self):
        return sum(v.final_amount for v in self.visits.all())
 
 
class Visit(models.Model):
    """
    Each time a customer makes a purchase, a Visit record is created.
    The customer is looked up (or created) by their phone number.
    """
    DISCOUNT_TYPE_CHOICES = (
        ('PERCENT', 'Percentage (%)'),
        ('AMOUNT', 'Fixed Amount (₹)'),
    )
 
    # FK uses Customer's default integer PK — safe with existing Invoice table
    Customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='visits'
    )
    Store    = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, related_name='visits')
    VisitDate = models.DateTimeField(default=timezone.now)
    BillAmount = models.DecimalField(max_digits=10, decimal_places=2)
    DiscountType = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default='PERCENT'
    )
    DiscountValue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Enter % value or flat ₹ amount depending on DiscountType"
    )
    Note = models.TextField(blank=True)
 
    class Meta:
        ordering = ['-VisitDate']
 
    def __str__(self):
        return f"{self.Customer.Name} – {self.VisitDate.date()} – ₹{self.final_amount}"
 
    @property
    def discount_amount(self):
        if self.DiscountType == 'PERCENT':
            return round(self.BillAmount * self.DiscountValue / 100, 2)
        return self.DiscountValue  # already a flat amount
 
    @property
    def final_amount(self):
        return max(self.BillAmount - self.discount_amount, 0)

class Service(models.Model):
    ServiceName = models.CharField(max_length=25)
    Cost = models.PositiveIntegerField()
    TimeStamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ServiceName
                 

class Invoice(models.Model):
    Customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    Store = models.ForeignKey(Store, on_delete=models.CASCADE)
    CreatedBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    BillingNumber = models.IntegerField(null=True, blank=True)
    Catagories = models.ManyToManyField(Service)

    Date = models.DateTimeField(auto_now_add=True)
    Note = models.TextField()

    def __str__(self):
        return str(self.BillingNumber)


@receiver(post_save, sender=Invoice)
def order_listing_update(sender, instance, created, **kwargs):
    if created and not instance.BillingNumber:
        instance.BillingNumber = 6060 + instance.id
        instance.save(update_fields=["BillingNumber"])

class Review(models.Model):

    RATING_CHOICES = (
        (1, '1 - Very Bad'),
        (2, '2 - Bad'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    )

    Customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    Store = models.ForeignKey(Store, on_delete=models.CASCADE)

    Service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    Employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)

    Rating = models.IntegerField(choices=RATING_CHOICES)
    Comment = models.TextField()

    CreatedAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.Customer.username} - {self.Rating}"
