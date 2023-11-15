from ..models import User
from django import forms


class LoginForm(forms.Form):
    # form fields
    email = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your email id'
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
