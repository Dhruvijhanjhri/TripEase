from django import forms

class TripPlannerForm(forms.Form):

    destination = forms.CharField(
        max_length=100
    )

    budget = forms.IntegerField(
        min_value=1000
    )

    days = forms.IntegerField(
        min_value=1,
        max_value=30
    )

    interests = forms.CharField(
        widget=forms.Textarea
    )