from django import forms
from parlour.models import *
from adminsection.models import *
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Username',
        'class':'user'   
    }))
    password = forms.CharField(strip=False,widget=forms.PasswordInput(attrs={
        
        'placeholder':'Password',
        'class':'lock'
    }))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            # authenticate() checks BOTH username and password at once
            self.user = authenticate(username=username, password=password)

            if self.user is None:
                # This covers both "User doesn't exist" AND "Wrong password"
                raise forms.ValidationError("Invalid username or password.")
            
            if not self.user.is_active:
                raise forms.ValidationError("This account is currently disabled.")

        return cleaned_data
    def get_user(self):
        return self.user



class AddServiceForm(forms.ModelForm):
    ServiceName = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Service Name',
        'label': "Service Name"
    }))
    Cost = forms.CharField(strip=False,widget=forms.TextInput(attrs={
        
        'placeholder': 'Cost',
        'label': "Cost"
    }))
    Note = forms.CharField( widget=forms.Textarea(attrs={'placeholder': 'Note'}))
    
    class Meta:

        model=Service

        fields =[
            'ServiceName',
            'Cost',
            'Note',
        ]


class CustomerVisitForm(forms.Form):
    """
    Single POS form: looks up customer by PhoneID (unique field),
    creates if new, then records a Visit.
    """
    phone = forms.CharField(
        max_length=11, label="Phone Number",
        widget=forms.TextInput(attrs={'placeholder': '9876543210', 'autofocus': True, 'class': 'form-control'})
    )
    name = forms.CharField(
        max_length=150, label="Customer Name",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    customer_note = forms.CharField(
        required=False, label="Customer Note",
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'})
    )
    bill_amount = forms.DecimalField(
        max_digits=10, decimal_places=2, label="Bill Amount (₹)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'})
    )
    discount_type = forms.ChoiceField(
        choices=Visit.DISCOUNT_TYPE_CHOICES, label="Discount Type",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    discount_value = forms.DecimalField(
        max_digits=10, decimal_places=2, initial=0, label="Discount Value",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'})
    )
    visit_note = forms.CharField(
        required=False, label="Visit / Bill Note",
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'})
    )
 
    def save(self):
        """
        Lookup by PhoneID (unique CharField).
        The Customer FK uses the integer PK internally — Invoice table is unaffected.
        Returns (customer, visit, is_new).
        """
        data = self.cleaned_data
        customer, created = Customer.objects.update_or_create(
            PhoneID=data['phone'],
            defaults={'Name': data['name'], 'Note': data['customer_note']}
        )
        visit = Visit.objects.create(
            Customer=customer,
            BillAmount=data['bill_amount'],
            DiscountType=data['discount_type'],
            DiscountValue=data['discount_value'],
            Note=data['visit_note'],
        )
        return customer, visit, created
 
 
class EditCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['Name', 'PhoneID', 'Note']
        labels = {'PhoneID': 'Phone Number'}
        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control'}),
            'PhoneID': forms.TextInput(attrs={'class': 'form-control'}),
            'Note': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
 


class AddCustomerForm(forms.ModelForm):

    Name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    Email = forms.CharField( widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    PhoneNumber = forms.CharField( widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    Note = forms.CharField( widget=forms.Textarea(attrs={'placeholder': 'Note'}))



    class Meta:

        model=Customer
        fields =[
            'Name',
            'Email',
            'PhoneNumber',
            'Note'
        ]          

    def clean_gender(self):
        Gender = self.cleaned_data.get('Gender')
        if not Gender:
            raise forms.ValidationError("Gender required")
        return Gender        
    
    def clean_details(self):
        Note = self.cleaned_data.get('Note')
        if not Note:
            raise forms.ValidationError("Note required")
        return Note    


class AddEmployeeForm(forms.ModelForm):

    Name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    Email = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    PhoneNumber = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    Note = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Note'}))
    JoiningDate = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'YYYY-MM-DD', 'type': 'date'}))
    Salary = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder': 'Salary'}))  # Add this

    class Meta:
        model = Employee
        fields = [
            'JoiningDate',
            'Salary',
            'Note'
        ]

    def clean_Note(self):
        Note = self.cleaned_data.get('Note')
        if not Note:
            raise forms.ValidationError("Note required")
        return Note


class AppointmentUpdateForm(forms.ModelForm):

    Note = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Note if needed'})
    )

    class Meta:
        model = Appointment
        fields = ['Service', 'Note', 'Remark']

    