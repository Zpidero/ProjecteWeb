from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password'] # Standard User fields