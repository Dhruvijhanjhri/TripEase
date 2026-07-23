from django import forms


class PackageSearchForm(forms.Form):

    destination = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter destination"}
        ),
    )


class PackageBookingForm(forms.Form):

    travel_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    travellers_count = forms.IntegerField(
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
