from django import forms
from .models import Airport, Flight
from django.core.exceptions import ValidationError
from datetime import date


class FlightSearchForm(forms.Form):
    """Flight search form"""
    CABIN_CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('business', 'Business'),
        ('first', 'First Class'),
    ]

    source = forms.ModelChoiceField(
        queryset=Airport.objects.all(),
        empty_label="Select departure airport",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'from'
        })
    )
    destination = forms.ModelChoiceField(
        queryset=Airport.objects.all(),
        empty_label="Select arrival airport",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'to'
        })
    )
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'date',
            'min': str(date.today())
        })
    )
    cabin_class = forms.ChoiceField(
        choices=CABIN_CLASS_CHOICES,
        initial='economy',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    passengers = forms.IntegerField(
        min_value=1,
        max_value=9,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '9'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get('source')
        destination = cleaned_data.get('destination')
        departure_date = cleaned_data.get('departure_date')

        if source and destination:
            if source == destination:
                raise ValidationError('Source and destination cannot be the same.')

        if departure_date:
            if departure_date < date.today():
                raise ValidationError('Departure date cannot be in the past.')

        return cleaned_data

