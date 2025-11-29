from django import forms
from .models import Payment


class PaymentForm(forms.Form):
    """Payment form"""
    PAYMENT_METHOD_CHOICES = [
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'payment-method-radio'
        })
    )
    
    # UPI fields
    upi_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'yourname@upi',
            'id': 'upi_id'
        })
    )
    
    # Card fields
    card_number = forms.CharField(
        required=False,
        max_length=16,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'id': 'card_number',
            'maxlength': '16'
        })
    )
    card_name = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cardholder Name',
            'id': 'card_name'
        })
    )
    card_expiry = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
            'id': 'card_expiry',
            'maxlength': '5'
        })
    )
    card_cvv = forms.CharField(
        required=False,
        max_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'CVV',
            'id': 'card_cvv',
            'maxlength': '3'
        })
    )
    
    # Net Banking fields
    bank_name = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'bank_name'
        }),
        choices=[
            ('', 'Select Bank'),
            ('sbi', 'State Bank of India'),
            ('hdfc', 'HDFC Bank'),
            ('icici', 'ICICI Bank'),
            ('axis', 'Axis Bank'),
            ('pnb', 'Punjab National Bank'),
        ]
    )

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method == 'upi':
            if not cleaned_data.get('upi_id'):
                raise forms.ValidationError('UPI ID is required for UPI payment.')
        elif payment_method == 'card':
            if not all([cleaned_data.get('card_number'), cleaned_data.get('card_name'), 
                       cleaned_data.get('card_expiry'), cleaned_data.get('card_cvv')]):
                raise forms.ValidationError('All card details are required.')
        elif payment_method == 'netbanking':
            if not cleaned_data.get('bank_name'):
                raise forms.ValidationError('Bank selection is required for Net Banking.')
        
        return cleaned_data

