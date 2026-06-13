from django import forms
from django.forms import formset_factory

from .models import HotelGuest


class HotelSearchForm(forms.Form):
    """Hotel search form"""

    destination = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'City, Area or Hotel Name'
            }
        )
    )

    check_in_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
    )

    check_out_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
    )

    guests = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    rooms = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )


class HotelGuestForm(forms.ModelForm):
    """Guest details form"""

    class Meta:
        model = HotelGuest

        fields = [
            'full_name',
            'age',
            'gender'
        ]

        widgets = {
            'full_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Guest Full Name'
                }
            ),

            'age': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'gender': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            )
        }


HotelGuestFormSet = formset_factory(
    HotelGuestForm,
    extra=1
)