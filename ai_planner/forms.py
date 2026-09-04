from django import forms


class TripPlannerForm(forms.Form):

    origin_city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "e.g. Bengaluru, Mumbai, Delhi",
            }
        ),
    )

    destination = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "e.g. Manali, Goa, Kashmir",
            }
        ),
    )

    budget = forms.IntegerField(
        min_value=1000,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Enter your budget",
            }
        ),
    )

    days = forms.IntegerField(
        min_value=1,
        max_value=30,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Number of days",
            }
        ),
    )

    interests = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Adventure, Snow, Local Food, Trekking, Lakes...",
            }
        ),
    )
