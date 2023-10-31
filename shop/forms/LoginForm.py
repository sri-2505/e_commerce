from ..models import User
from django import forms


class LoginForm(forms.Form):
    # form fields
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'validationCustom02',
        'placeholder': 'Please enter you name here'
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Please enter your password here'
    }))

    class Meta:
        model = User
        fields = [
            'email',
            'password',
        ]
