import datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# from django.db.models.functions import datetime
from django.forms import ModelForm

from YAASApp.models import Profile, Auction, Bid


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


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


class ConfAuctionForm(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)
    b_title = forms.CharField(widget=forms.HiddenInput())
    b_description = forms.CharField(widget=forms.HiddenInput())
    b_minimum_price = forms.FloatField(widget=forms.HiddenInput())
    b_deadline = forms.DateTimeField(widget=forms.HiddenInput())

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ('bid_price',)
