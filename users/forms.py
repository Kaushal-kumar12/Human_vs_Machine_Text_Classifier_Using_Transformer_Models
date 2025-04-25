from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

# Registration Form
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

# ✅ Login Form (Fix the missing import issue)
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class TextForm(forms.Form):
    text_input = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter text here...', 'rows': 5, 'cols': 50}), required=True)