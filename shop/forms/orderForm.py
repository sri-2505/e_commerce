from ..models import Order
from django import forms
from utils.constants import *
from django.core.validators import RegexValidator


class OrderForm(forms.ModelForm):
    # form fields
    state = forms.ChoiceField(
        choices=STATES + [('', 'Select an option')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'state',
            'placeholder': 'Enter your state'
        })
    )

    district = forms.ChoiceField(
        choices=TAMIL_NADU_DISTRICTS + [('', 'Select an option')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'district',
            'placeholder': 'Enter the district'
        })
    )

    city = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the city name'
        })
    )

    street_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'A - 75, Example start name'
        })
    )

    pincode = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Please enter you name here'
        })
    )

    payment_type = forms.ChoiceField(
        choices=PAYMENT_TYPES,
        widget=forms.RadioSelect()
    )

    class Meta:
        model = Order
        fields = [
            'state',
            'district',
            'city',
            'street_name',
            'pincode',
            'payment_type'
        ]
"""
    Form validation
"""


