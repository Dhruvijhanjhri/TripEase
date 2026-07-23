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
                "style": "height:55px;",
            }
        ),
    )

    check_in = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control", "style": "height:55px;"}
        )
    )

    check_out = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control", "style": "height:55px;"}
        )
    )

    guests = forms.IntegerField(
        initial=2,
        min_value=1,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "style": "height:55px;"}
        ),
    )

    rooms = forms.IntegerField(
        initial=1,
        min_value=1,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "style": "height:55px;"}
        ),
    )


class HotelGuestForm(forms.ModelForm):

    class Meta:
        model = HotelGuest

        fields = ["full_name", "age", "gender"]

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "age": forms.NumberInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
        }


HotelGuestFormSet = modelformset_factory(HotelGuest, form=HotelGuestForm, extra=1)


class HotelPaymentForm(forms.Form):

    PAYMENT_METHOD_CHOICES = [
        ("upi", "UPI"),
        ("card", "Credit/Debit Card"),
        ("netbanking", "Net Banking"),
        ("wallet", "Wallet"),
    ]

    BANK_CHOICES = [
        ("", "Select Bank"),
        ("sbi", "State Bank of India"),
        ("hdfc", "HDFC Bank"),
        ("icici", "ICICI Bank"),
        ("axis", "Axis Bank"),
        ("kotak", "Kotak Mahindra Bank"),
    ]

    WALLET_CHOICES = [
        ("", "Select Wallet"),
        ("paytm", "Paytm"),
        ("phonepe", "PhonePe"),
        ("googlepay", "Google Pay"),
        ("amazonpay", "Amazon Pay"),
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect
    )

    upi_id = forms.CharField(required=False)
    card_number = forms.CharField(required=False)
    cardholder_name = forms.CharField(required=False)
    card_expiry = forms.CharField(required=False)
    card_cvv = forms.CharField(required=False)
    bank_name = forms.ChoiceField(choices=BANK_CHOICES, required=False)
    wallet_name = forms.ChoiceField(choices=WALLET_CHOICES, required=False)

    def clean(self):
        cleaned_data = super().clean()

        payment_method = cleaned_data.get("payment_method")

        if payment_method == "upi" and not cleaned_data.get("upi_id"):
            self.add_error("upi_id", "Enter a UPI ID.")
        elif payment_method == "card":
            required_fields = [
                ("card_number", "Enter the card number."),
                ("cardholder_name", "Enter the cardholder name."),
                ("card_expiry", "Enter the expiry date."),
                ("card_cvv", "Enter the CVV."),
            ]

            for field_name, error_message in required_fields:
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, error_message)
        elif payment_method == "netbanking" and not cleaned_data.get("bank_name"):
            self.add_error("bank_name", "Select a bank.")
        elif payment_method == "wallet" and not cleaned_data.get("wallet_name"):
            self.add_error("wallet_name", "Select a wallet.")

        return cleaned_data
