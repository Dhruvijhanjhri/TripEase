from django import forms
from .models import Passenger


class PassengerForm(forms.ModelForm):
    """Form for passenger details"""
    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'age', 'gender']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name',
                'required': True
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Age',
                'min': '1',
                'max': '120',
                'required': True
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
        }


PassengerFormSet = forms.formset_factory(PassengerForm, extra=0, min_num=1)



