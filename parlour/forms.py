from django import forms
from parlour.models import Appointment


class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment
        fields = [
            'Name',
            'Email',
            'PhoneNumber',
            'Service',
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
            'AppointmentDate': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'AppointmentTime': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
        }
