from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={"placeholder": "Usuario"}),
    )
    password = forms.CharField(
        label="Contrasena",
        widget=forms.PasswordInput(attrs={"placeholder": "Contrasena"}),
    )


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "tu@email.com"}),
    )

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")

