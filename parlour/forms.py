from django import forms
from parlour.models import Appoinment


class AppoinmentForm(forms.ModelForm):

    class Meta:
        model = Appoinment
        fields = [
            'Name',
            'Email',
            'PhoneNumber',
            'Service',
            'AppoinmentDate',
            'AppoinmentTime',
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
            'AppoinmentDate': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'AppoinmentTime': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
        }
