# FILE: accounts/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Profile

# Secret passcode required to register a Teacher account
INSTRUCTOR_SECRET_KEY = "FACULTY2026"


class StudentRegistrationForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'roleSelect'})
    )
    instructor_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'instructorKeyField',
            'placeholder': 'Enter secret passcode (Teachers only)'
        }),
        help_text="Required only when registering as an Instructor / Teacher."
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create strong password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unique username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        role = cleaned_data.get("role")
        key = cleaned_data.get("instructor_key")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        if role == 'teacher':
            if not key:
                self.add_error('instructor_key', "Instructor secret passcode is required to create a Teacher account.")
            elif key != INSTRUCTOR_SECRET_KEY:
                self.add_error('instructor_key', "Invalid instructor verification passcode. Access denied.")

        return cleaned_data


# Alias for backward compatibility
RegistrationForm = StudentRegistrationForm


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
        }