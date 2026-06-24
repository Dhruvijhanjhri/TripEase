from django import forms
from .models import HotelReview, PackageReview, FlightReview


class HotelReviewForm(forms.ModelForm):
    class Meta:
        model = HotelReview
        fields = ["rating", "review_text"]
        widgets = {
            "rating": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 5
            }),
            "review_text": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Write your review..."
            }),
        }


class PackageReviewForm(forms.ModelForm):
    class Meta:
        model = PackageReview
        fields = ["rating", "review_text"]
        widgets = {
            "rating": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 5
            }),
            "review_text": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Write your review..."
            }),
        }


class FlightReviewForm(forms.ModelForm):
    class Meta:
        model = FlightReview
        fields = ["rating", "review_text"]
        widgets = {
            "rating": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 5
            }),
            "review_text": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Write your review..."
            }),
        }