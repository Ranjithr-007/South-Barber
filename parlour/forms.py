from django import forms
from parlour.models import Appointment, Service, Store  

class AppointmentForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set querysets for foreign key fields
        self.fields['Service'].queryset = Service.objects.all()
        self.fields['Store'].queryset = Store.objects.all()
        
        # Add empty label for better UX
        self.fields['Service'].empty_label = "Select Service"
        self.fields['Store'].empty_label = "Select Store"

    class Meta:
        model = Appointment
        fields = [
            'Name',
            'Email',
            'PhoneNumber',
            'Service',
            'Store',        
            'AppointmentDate',
            'AppointmentTime',
        ]

        widgets = {
            'Name': forms.TextInput(attrs={
                'placeholder': 'Name',
                'class': 'form-control'
            }),
            'Email': forms.EmailInput(attrs={
                'placeholder': 'Email',
                'class': 'form-control'
            }),
            'PhoneNumber': forms.TextInput(attrs={
                'placeholder': 'Phone Number',
                'class': 'form-control'
            }),
            'Service': forms.Select(attrs={
                'class': 'form-control'
            }),
            'Store': forms.Select(attrs={       
                'class': 'form-control'
            }),
            'AppointmentDate': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'AppointmentTime': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
        }