from django import forms


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