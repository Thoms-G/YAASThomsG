from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from YAASApp.models import Profile


class UserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')


class ProfileForm(ModelForm):
    preferred_language = forms.ChoiceField(choices=(('EN', 'English'), ('FR', 'Francais')))

    class Meta:
        model = Profile
        fields = ('preferred_language',)


class UpdateUserForm(ModelForm):
    class Meta:
        model = User
        fields = ('email', 'password')


