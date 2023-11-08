from django.contrib.auth.forms import UserCreationForm
from ..models import User
from django import forms


# over writing the UserCreationForm
# TODO::add more user registration fields(customer user model)
class CustomUserForm(UserCreationForm):
    # form fields widgets
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'validationCustom02', 'placeholder': 'Please enter you name here'}
    ))

    email = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'name@example.com'}
    ))

    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Please enter your password here'}
    ))

    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Please enter you password here'}
    ))

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]
