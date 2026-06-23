from django import forms

from .models import (
    HotelReview,
    PackageReview
)


class HotelReviewForm(forms.ModelForm):

    class Meta:

        model = HotelReview

        fields = [
            "rating",
            "review_text"
        ]

        widgets = {

            "rating": forms.Select(
                choices=[
                    (1, "⭐ 1"),
                    (2, "⭐⭐ 2"),
                    (3, "⭐⭐⭐ 3"),
                    (4, "⭐⭐⭐⭐ 4"),
                    (5, "⭐⭐⭐⭐⭐ 5"),
                ]
            ),

            "review_text": forms.Textarea(
                attrs={
                    "rows": 4
                }
            )
        }


class PackageReviewForm(forms.ModelForm):

    class Meta:

        model = PackageReview

        fields = [
            "rating",
            "review_text"
        ]

        widgets = {

            "rating": forms.Select(
                choices=[
                    (1, "⭐ 1"),
                    (2, "⭐⭐ 2"),
                    (3, "⭐⭐⭐ 3"),
                    (4, "⭐⭐⭐⭐ 4"),
                    (5, "⭐⭐⭐⭐⭐ 5"),
                ]
            ),

            "review_text": forms.Textarea(
                attrs={
                    "rows": 4
                }
            )
        }