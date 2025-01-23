from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django import forms
import re

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'public_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.initial['username'] = self.instance.username.lstrip('@')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            raise forms.ValidationError("Имя пользователя может содержать только латинские буквы и цифры.")
        if CustomUser.objects.filter(username='@' + username.lower()).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует.")
        if not username.startswith('@'):
            username = f'@{username}'
        return username.lower()

class CustomUserEditionForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username','public_name', 'status','avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['username'] = self.instance.username.lstrip('@')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            raise forms.ValidationError("Имя пользователя может содержать только латинские буквы и цифры.")

        if self.instance and self.instance.username.lstrip('@') == username:
            return username

        if CustomUser.objects.filter(username='@' + username.lower()).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует.")
        return username

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.username = '@' + self.cleaned_data['username']
        if commit:
            instance.save()
        return instance

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            raise forms.ValidationError("Имя пользователя может содержать только латинские буквы и цифры.")
        if not username.startswith('@'):
            username = f'@{username}'
        return username.lower()

class CustomUserConfirmationForm(forms.Form):
    confirmation_code = forms.CharField(max_length=6, required=True)



