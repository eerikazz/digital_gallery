# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label="First name")
    last_name  = forms.CharField(max_length=150, required=True, label="Last name")
    email      = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model  = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
        )  # password1 & password2 come from the parent class

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name  = self.cleaned_data["last_name"]
        user.email      = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
