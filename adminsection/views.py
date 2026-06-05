from django.shortcuts import render, get_object_or_404, redirect
from adminsection.forms import *
from adminsection.models import *
from parlour.models import Appointment
from django.contrib import auth
from django.urls import reverse
from django.db.models import Q
from django.db.models import Sum
from datetime import date, timedelta
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
import string
from decimal import Decimal
import json

def signin(request):
    """
        LogIn page for Admin/Staff
    """ 
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            print(form.errors)
    
    context = {'form': form}
    return render(request, 'adminsection/signin.html', context)

def get_user_stores(request):
    """Get stores accessible to the current user"""
    if request.user.is_superuser:
        # Superusers can see all stores
        return Store.objects.all(), True
    
    # Regular staff - get their assigned stores
    store_staff = StoreStaff.objects.filter(user=request.user).select_related('store')
    stores = [ss.store for ss in store_staff]
    
    # Check if user is owner of any store (can see all)
    is_owner = any(ss.is_owner for ss in store_staff)
    if is_owner:
        stores = Store.objects.all()
    
    return stores, is_owner

def get_active_store(request):
    """Get currently selected store from session"""
    stores, is_owner = get_user_stores(request)
    
    if not stores:
        return None, stores, is_owner
    
    # If only one store, use it
    if len(stores) == 1:
        return stores[0], stores, is_owner
    
    # Get store from session
    store_id = request.session.get('active_store_id')
    if store_id:
        try:
            active_store = next((s for s in stores if str(s.id) == str(store_id)), stores[0])
            return active_store, stores, is_owner
        except:
            pass
    
    return stores[0], stores, is_owner

@staff_member_required
def dashboard(request):
    """
    Adminsection Dashboard with multi-store support.
    """
    active_store, user_stores, is_owner = get_active_store(request)
    
    # Base querysets filtered by active store
    if active_store:
        all_visits = Visit.objects.filter(Store=active_store).select_related('Customer')
        all_appointments = Appointment.objects.filter(Store=active_store)
        all_customers = Customer.objects.filter(
            visits__Store=active_store
        ).distinct().prefetch_related('visits')
    else:
        all_visits = Visit.objects.none()
        all_appointments = Appointment.objects.none()
        all_customers = Customer.objects.none()
    
    # Statistics
    total_appointment = all_appointments.count()
    total_service = Service.objects.all().count()
    total_employee = Employee.objects.all().count()
    total_customer = all_customers.count()
    
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Today's appointments (filtered by store)
    todays_appointments = all_appointments.filter(
        AppointmentDate=today
    ).select_related('Service').order_by('AppointmentTime')
    
    # Recent visits (filtered by store)
    recent_visits = all_visits.select_related('Customer').order_by('-VisitDate')[:10]
    
    # Sales aggregates
    def sales_sum(qs):
        total = Decimal('0')
        for v in qs:
            total += v.final_amount
        return float(total)
    
    today_visits = all_visits.filter(VisitDate__date=today)
    week_visits = all_visits.filter(VisitDate__date__gte=week_start)
    month_visits = all_visits.filter(VisitDate__date__gte=month_start)
    
    today_sales = sales_sum(today_visits)
    weekly_sales = sales_sum(week_visits)
    monthly_sales = sales_sum(month_visits)
    
    # Retention rate (customers who visited this store more than once)
    total_customers = all_customers.count()
    retained = 0
    
    for customer in all_customers:
        # Count only visits to this specific store
        store_visits = customer.visits.filter(Store=active_store).count() if active_store else 0
        if store_visits > 1:
            retained += 1
    
    retention_rate = round((retained / total_customers * 100), 1) if total_customers else 0
    
    # Weekly chart data (Mon-Sun)
    week_labels, week_data = [], []
    for i in range(7):
        day = week_start + timedelta(days=i)
        label = day.strftime('%a')
        day_visits = all_visits.filter(VisitDate__date=day)
        week_labels.append(label)
        week_data.append(sales_sum(day_visits))
    
    # Monthly chart data (last 4 weeks)
    month_labels, month_data = [], []
    for i in range(4):
        wk_start = month_start + timedelta(weeks=i)
        wk_end = wk_start + timedelta(days=6)
        label = f"Wk {i+1}"
        wk_visits = all_visits.filter(
            VisitDate__date__gte=wk_start,
            VisitDate__date__lte=wk_end
        )
        month_labels.append(label)
        month_data.append(sales_sum(wk_visits))
    
    # Yearly chart data
    year = today.year
    year_labels, year_data = [], []
    for m in range(1, 13):
        month_visits_yr = all_visits.filter(
            VisitDate__year=year, 
            VisitDate__month=m
        )
        year_labels.append(date(year, m, 1).strftime('%b'))
        year_data.append(sales_sum(month_visits_yr))
    
    context = {
        'active_store': active_store,
        'user_stores': user_stores,
        'is_owner': is_owner,
        'total_appointment': total_appointment,
        'total_service': total_service,
        'total_employee': total_employee,
        'total_customer': total_customer,
        'todays_appointments': todays_appointments,
        'recent_visits': recent_visits,
        'today_sales': today_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        'retention_rate': retention_rate,
        'total_customers': total_customers,
        'retained_customers': retained,
        'week_labels': json.dumps(week_labels),
        'week_data': json.dumps(week_data),
        'month_labels': json.dumps(month_labels),
        'month_data': json.dumps(month_data),
        'year_labels': json.dumps(year_labels),
        'year_data': json.dumps(year_data),
    }
    return render(request, 'adminsection/admindashboard.html', context)

@staff_member_required
def switch_store(request, store_id):
    """Switch active store"""
    request.session['active_store_id'] = str(store_id)
    
    # Get the referring page
    next_url = request.GET.get('next', 'dashboard')
    return redirect(next_url)


@staff_member_required
def addservice(request):
    """
        Admin can add Service and Price.
    """ 
    form = AddServiceForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('manageservices')
    context = {
        'form': form
    }

    return render(request, 'adminsection/add-services.html', context)


@staff_member_required
def manageservices(request):
    """
        Admin can check the service list.
    """ 
    Services = Service.objects.order_by('-TimeStamp')

    context = {
        'Services': Services
    }
    return render(request, 'adminsection/manage-services.html', context)


@staff_member_required
def updateservice(request, id):
    """
        Admin can update any service.
    """ 
    service = get_object_or_404(Service, id=id)
    form = AddServiceForm(request.POST or None, instance=service)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('manageservices')

    context = {
        'form': form
    }
    return render(request, 'adminsection/edit-services.html', context)


@staff_member_required
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    service.delete()
    return redirect('manageservices') 


@staff_member_required
def addcustomer(request):
    """
        Admin can add customer details.
    """ 
    form = AddCustomerForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('customerlist')
    context = {

        'form': form,
    }
    return render(request, 'adminsection/add-customer.html', context)


@staff_member_required
def addemployee(request):
    active_store, user_stores, is_owner = get_active_store(request)

    form = AddEmployeeForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['Email']
            if User.objects.filter(username=email).exists():
                form.add_error('Email', 'An employee with this email already exists.')
            else:
                employee = form.save(commit=False)
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=form.cleaned_data['Name'],
                )
                employee.User = user
                employee.EmployeeID = 'EMP' + str(User.objects.count()).zfill(4)
                employee.Store = active_store
                employee.save()
                return redirect('employeelist')

    return render(request, 'adminsection/add-employee.html', {
        'form': form,
        'active_store': active_store,
    })

@staff_member_required
def employeelist(request):
    active_store, user_stores, is_owner = get_active_store(request)

    employee = Employee.objects.filter(
        Store=active_store
    ).order_by('-JoiningDate')

    return render(request, 'adminsection/employee-list.html', {
        'employee': employee,
        'active_store': active_store,
        'user_stores': user_stores,
        'is_owner': is_owner,
    })

@staff_member_required
def editemployee(request, id):
    """
        Edit customer details.
    """ 

    customer = get_object_or_404(Customer, id=id)
    form = AddCustomerForm(request.POST or None, instance=customer)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            print(form)
            return redirect('employeelist')

    context = {
        'form': form
    }
    return render(request, 'adminsection/edit-employee-detailed.html', context)


@staff_member_required
def deleteemployee(request, id):
    customer = get_object_or_404(Customer, id=id)
    customer.delete()
    return redirect('employeelist')


@staff_member_required
def customerlist(request):
    active_store, user_stores, is_owner = get_active_store(request)
    
    # Get customers who have visited this store
    store_customer_ids = Visit.objects.filter(
        Store=active_store
    ).values_list('Customer', flat=True).distinct()
    
    CustomerList = Customer.objects.filter(
        PhoneID__in=store_customer_ids
    ).order_by('-CreateDate')

    letters = list(string.ascii_uppercase)
    customers_with_letters = []
    for i, customer in enumerate(CustomerList):
        letter_id = letters[i % 26]
        customers_with_letters.append({
            'customer': customer,
            'letter_id': letter_id
        })

    return render(request, 'adminsection/customer-list.html', {
        'customers_with_letters': customers_with_letters,
        'active_store': active_store,
        'user_stores': user_stores,
        'is_owner': is_owner,
    })


@staff_member_required
def addcustomer(request):
    form = AddCustomerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        customer = form.save()
        return redirect('customer_detail', id=customer.PhoneID)
    return render(request, 'adminsection/add-customer.html', {'form': form})


@staff_member_required
def editcustomer(request, id):
    customer = get_object_or_404(Customer, PhoneID=id)
    form = AddCustomerForm(request.POST or None, instance=customer)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('customer_detail', id=id)
    return render(request, 'adminsection/edit-customer-detailed.html', {'form': form, 'customer': customer})


@staff_member_required
def deletecustomer(request, id):
    customer = get_object_or_404(Customer, PhoneID=id)
    customer.delete()
    return redirect('customerlist')


@staff_member_required
def customer_detail(request, id):
    customer = get_object_or_404(Customer, PhoneID=id)
    visits = customer.visits.order_by('-VisitDate')
    return render(request, 'adminsection/customer-detail.html', {
        'customer': customer,
        'visits': visits,
    })


@staff_member_required
def add_visit(request, id):
    customer = get_object_or_404(Customer, PhoneID=id)
    active_store, _, _ = get_active_store(request)

    if not active_store:
        messages.error(request, "No store assigned to you.")
        return redirect('dashboard')

    if request.method == 'POST':
        bill_amount = Decimal(request.POST.get('bill_amount', 0))
        discount_type = request.POST.get('discount_type', 'PERCENT')
        discount_value = Decimal(request.POST.get('discount_value', 0))
        note = request.POST.get('note', '')

        Visit.objects.create(
            Customer=customer,
            Store=active_store,
            BillAmount=bill_amount,
            DiscountType=discount_type,
            DiscountValue=discount_value,
            Note=note,
        )
        return redirect('customer_detail', id=id)

    return render(request, 'adminsection/add-visit.html', {'customer': customer})
@staff_member_required
def lookup_customer(request):
    """Manager enters phone number to find or create customer."""
    if request.method == 'POST':
        phone = request.POST.get('phone_number', '').strip()
        name = request.POST.get('name', 'Unknown').strip()

        customer, created = Customer.objects.get_or_create(
            PhoneNumber=phone,
            defaults={'Name': name}
        )
        return redirect('customer_detail', id=customer.PhoneID)

    return render(request, 'adminsection/lookup-customer.html')


@staff_member_required
def assignservices(request, id):
    """
       Can assign services for  Customer.
    """ 

    customer = get_object_or_404(Customer, id=id)
    Services = Service.objects.order_by('-TimeStamp')

    if request.method == 'POST':
        # total_price=request.POST['total_price']
        # discount_price=request.POST['discount_price']
        serviceid = request.POST.getlist('serviceid')

        # if discount_price:
        #     final_price=int(total_price)-int(discount_price)
        #     a1=Invoice(Note=final_price)

        # else:
        #     a1=Invoice()

        instance = Invoice()
        instance.Customer = customer
        instance.save()
        for obj in serviceid:
            instance.Catagories.add(obj)

        return redirect(reverse("viewinvoice", kwargs={
            'id': instance.id
        }))
    context = {
        'Services': Services,
        'customer': customer
    }

    return render(request, 'adminsection/add-customer-services.html', context)

@staff_member_required
def allappointment(request):
    """Appointment Lists - filtered by active store.
    """
    active_store, user_stores, is_owner = get_active_store(request)

    Appointments = Appointment.objects.filter(
        Store=active_store
    ).order_by('-ApplyDate')

    return render(request, 'adminsection/appointments.html', {
        'Appointments': Appointments,
        'active_store': active_store,
        'user_stores': user_stores,
        'is_owner': is_owner,
    })

@staff_member_required
def today_appointment_detail(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related('Service'),
        id=pk
    )
    return render(request, 'adminsection/today_appointments.html', {
        'appt': appointment,
    })

@staff_member_required
def viewappointment(request, id):
    """
        View appointment.
    """ 

    Appointments = get_object_or_404(Appointment, id=id)
    form = AppointmentUpdateForm(request.POST or None, instance=Appointments)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            # return redirect('manageservices')
    context = {
        'Appointment': Appointments,
        'form': form
    }
    return render(request, 'adminsection/view-appointment.html', context)

@staff_member_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.delete()
    return redirect('allappointment')

@staff_member_required
def newappointment(request):
    """
        New appointments list.
    """ 

    Acceptedappointments = Appointment.objects.filter(Remark='')
    context = {
        'Acceptedappointments': Acceptedappointments,
    }
    return render(request, 'adminsection/new-appointment.html', context)


@staff_member_required
def acceptedappointment(request):
    """
        Accepted appointments list.
    """ 

    Acceptedappointments = Appointment.objects.filter(Remark=1)

    context = {
        'Acceptedappointments': Acceptedappointments,
    }
    return render(request, 'adminsection/accepted-appointment.html', context)


@staff_member_required
def rejectedappointment(request):
    """
        Rejected appointments.
    """ 
    Rejectedtedappointments = Appointment.objects.filter(Remark=0)

    context = {
        'Rejectedtedappointments': Rejectedtedappointments,
    }
    return render(request, 'adminsection/rejected-appointment.html', context)


@staff_member_required
def invoices(request):
    """
        Invoice lists.
    """ 

    invoices = Invoice.objects.order_by('-id')

    context = {
        'invoices': invoices
    }
    return render(request, 'adminsection/invoices.html', context)


@staff_member_required
def viewinvoice(request, id):
    """
        view Invoice .
    """ 

    invoice = get_object_or_404(Invoice, id=id)
    total = Invoice.objects.filter(id=id).aggregate(Sum('Catagories__Cost'))

    context = {
        'invoice': invoice,
        'total': total
    }
    return render(request, 'adminsection/view-invoice.html', context)


@staff_member_required
def searchappointment(request):
    appointment_list = ''
    query = request.GET.get('searchdata')
    if query:
        appointment_list = Appointment.objects.all()
        appointment_list = appointment_list.filter(
            Q(AppointmentNumber__iexact=query) |
            Q(Name__icontains=query) |
            Q(Email__iexact=query)
        ).distinct()

    context = {

        'appointment_list': appointment_list,
        'query': query
    }

    return render(request, 'adminsection/search-appointment.html', context)


@staff_member_required
def searchinvoices(request):

    query = request.GET.get('searchdata')

    invoice = Invoice.objects.filter(BillingNumber=query)

    context = {
        'invoice': invoice,
        'query': query
    }
    return render(request, 'adminsection/search-invoices.html', context)


@staff_member_required
def bwdatesreportsds(request):

    invoice_list = ''
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date and to_date:

        invoice_list = Invoice.objects.all()

        invoice_list = invoice_list.filter(
            Q(Date__gte=from_date),
            Q(Date__lte=to_date)
        ).distinct()
    context = {

        'invoice_list': invoice_list,
        'from_date': from_date,
        'to_date': to_date
    }

    return render(request, 'adminsection/bwdates-reports-ds.html', context)


@staff_member_required
def profile(request):
    return render(request, 'adminsection/admin-profile.html')


@staff_member_required
def changepassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'adminsection/change-password.html', {
        'form': form
    })


def forgetpassword(request):
    return render(request, 'adminsection/forget-password.html')


def contactus(request):
    return render(request, 'adminsection/contact-us.html')


@staff_member_required
def adminprofile(request):
    return render(request, 'adminsection/admin-profile.html')


def logout(request):
    auth.logout(request)
    return redirect('signin')
