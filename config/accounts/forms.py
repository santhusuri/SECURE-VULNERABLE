from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, VulnUser


class RegistrationForm(UserCreationForm):
    """
    Secure user registration form:
    - Uses Django's built-in UserCreationForm (with password hashing).
    - Validates username, email, and password strength.
    """

    email = forms.EmailField(
        required=True,
        help_text="Required. Enter a valid email address."
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "address", "phone")


class LoginForm(AuthenticationForm):
    """
    Secure login form:
    - Relies on Django's built-in authentication system.
    """
    pass


class VulnRegistrationForm(forms.ModelForm):
    """
    Vulnerable user registration form:
    - Stores passwords in plaintext.
    - Skips built-in validations.
    - Intended ONLY for demonstrating insecure practices in lab mode.
    """

    class Meta:
        model = VulnUser
        fields = ("username", "email", "password")

    # override widgets for more academic clarity
    password = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Enter password in plaintext"}),
        help_text="⚠ Stored without hashing (for demo only)."
    )
