from django import forms
from django.forms import modelformset_factory

from .models import HotelGuest


class HotelSearchForm(forms.Form):

    destination = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter city",
                "style": "height:55px;"
            }
        )
    )

    check_in = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "style": "height:55px;"
            }
        )
    )

    check_out = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "style": "height:55px;"
            }
        )
    )

    guests = forms.IntegerField(
        initial=2,
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "style": "height:55px;"
            }
        )
    )

    rooms = forms.IntegerField(
        initial=1,
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "style": "height:55px;"
            }
        )
    )


class HotelGuestForm(forms.ModelForm):

    class Meta:
        model = HotelGuest

        fields = [
            "full_name",
            "age",
            "gender"
        ]

        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "age": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),
        }


HotelGuestFormSet = modelformset_factory(
    HotelGuest,
    form=HotelGuestForm,
    extra=1
)