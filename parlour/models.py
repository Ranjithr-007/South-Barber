from django.db import models
from adminsection.models import Service
from adminsection.models import Store
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.

class Appointment(models.Model):


    Store = models.ForeignKey(Store, on_delete=models.CASCADE)
    Name = models.CharField(max_length=50)
    Email = models.EmailField()
    PhoneNumber = models.CharField(max_length=11)
    Service = models.ForeignKey(Service, on_delete=models.CASCADE)
    Note = models.TextField(blank=True)
    AppointmentDate = models.DateField()
    AppointmentTime = models.TimeField()  
    ApplyDate = models.DateTimeField(auto_now_add=True)
    RemarkDate = models.DateTimeField(auto_now=True)
    AppointmentNumber = models.IntegerField(null=True, blank=True)
    REMARK_CHOICES = (
        ('1', 'Accepted'),
        ('0', 'Rejected'),
    )
    Remark = models.CharField(max_length=1, choices=REMARK_CHOICES, blank=True)
    def __str__(self):
        return self.Name



@receiver(post_save, sender=Appointment)
def appointment_listing_update(sender, instance, created, **kwargs):
    appointmentnumber = 6000
    if created:
        instance.AppointmentNumber = appointmentnumber + instance.id
        instance.save()