from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save
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

    def __str__(self):
        return self.User.username

class Customer(models.Model):
    User = models.OneToOneField(User, on_delete=models.CASCADE)
    PhoneNumber = models.CharField(max_length=11)
    Gender = models.CharField(max_length=1, choices=(('0','Male'),('1','Female')))
    Note = models.TextField(blank=True)
    CreateDate = models.DateTimeField(auto_now_add=True)
    UpdateDate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.User.username


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
