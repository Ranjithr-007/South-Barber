from django.contrib import admin
from django.urls import path , include
from adminsection import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('signin/', views.signin, name='signin'),

    
    path('service/', views.addservice, name='addservices'),
    path('manageservices/', views.manageservices, name='manageservices'),
    path('updateservice/<int:id>/', views.updateservice, name='updateservice'),
    path('delete-service/<int:service_id>/', views.delete_service, name='delete_service'),
    
    path('addemployee/', views.addemployee, name='addemployee'),
    path('employeelist/', views.employeelist, name='employeelist'),
    path('editemployee/<int:id>/', views.editemployee, name='editemployee'),
    path('delete-employee/<int:id>/', views.deleteemployee, name='deleteemployee'),
    
    
    path('addcustomer/', views.addcustomer, name='addcustomer'),
    path('customerlist/', views.customerlist, name='customerlist'),
    path('editcustomer/<uuid:id>/', views.editcustomer, name='editcustomer'),
    path('delete-customer/<uuid:id>/', views.deletecustomer, name='deletecustomer'),
    path('customer/<uuid:id>/', views.customer_detail, name='customer_detail'),
    path('customer/<uuid:id>/add-visit/', views.add_visit, name='add_visit'),
    path('lookup-customer/', views.lookup_customer, name='lookup_customer'),

    
    path('assignservices/<int:id>/', views.assignservices, name='assignservices'),
    path('bwdatesreportsds/', views.bwdatesreportsds, name='bwdatesreportsds'),
    path('appointment/today/detail/<int:pk>/', views.today_appointment_detail, name='todayappointmentdetail'),
    path('allappointment/', views.allappointment, name='allappointment'),
    path('viewappointment/<int:id>/', views.viewappointment, name='viewappointment'),
    path('delete-appointment/<int:appointment_id>/', views.delete_appointment, name='deleteappointment'),
    path('newappointment/', views.newappointment, name='newappointment'),
    path('acceptedappointment/', views.acceptedappointment, name='acceptedappointment'),
    path('rejectedappointment/', views.rejectedappointment, name='rejectedappointment'),
    path('invoices/', views.invoices, name='invoices'),
    path('viewinvoice/<int:id>', views.viewinvoice, name='viewinvoice'),
    path('searchappointment/', views.searchappointment, name='searchappointment'),
    path('searchinvoices/', views.searchinvoices, name='searchinvoices'),
    path('adminprofile/', views.adminprofile, name='adminprofile'),
    path('changepassword/', views.changepassword, name='changepassword'),
    path('forgetpassword/', views.forgetpassword, name='forgetpassword'),
    path('contactus/', views.contactus, name='contactus'),
    path('logout/', views.logout, name='logout'),

]
