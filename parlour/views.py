from django.shortcuts import render,get_object_or_404,redirect
from parlour.forms import AppoinmentForm
from parlour.models import *
from adminsection.models import Service
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render
from .forms import AppoinmentForm

def home(request):

    """
        Provides the ability to make an appoinment via user
    """
    services = Service.objects.all()
    form     = AppoinmentForm(request.POST or None)
      
    if request.method=='POST':
       
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            form.save_m2m()
         
            return redirect(reverse("thankyou", kwargs={
                'id': form.instance.id
            }))

    context={
 
            'form':form,
            'services':services,
            }
    return render(request,'website/index.html',context)


def services(request):
    """
        Listing Page for Services
    """
    services = Service.objects.all()
    context={
        
            'services':services,
    }
    return render(request,'website/services.html',context)


def about(request):
    """
        About Page
    """  
    return render(request,'website/about.html')


def contact(request):
    """
        About Page
    """  
    return render(request,'website/contact.html')


def appointment_view(request):
    print(request.POST)
    if request.method == "POST":
        form = AppoinmentForm(request.POST)

        if form.is_valid():
            form.save()
            return JsonResponse({
                "status": "success",
                "message": "Your appointment successfully completed!"
            })

        else:
            return JsonResponse({
                "status": "error",
                "errors": form.errors
            }, status=400)


    else:
        form = AppoinmentForm()

    return render(request, "website/appointment.html", {"form": form})

