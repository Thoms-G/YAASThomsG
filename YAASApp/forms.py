import datetime
from django import forms
from django.contrib.auth.models import User
#from django.db.models.functions import datetime
from django.forms import ModelForm

from YAASApp.models import Profile, Auction


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


class AuctionForm(ModelForm):
    title = forms.CharField(required=True)
    deadline = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M:%S'], required=False,
                                   help_text='Format dd/mm/YY HH:MM:SS')

    class Meta:
        model = Auction
        fields = ('title', 'description', 'minimum_price', 'deadline')
