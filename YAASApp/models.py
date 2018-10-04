import datetime
from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    preferred_language = models.CharField(max_length=2, choices=(('EN', 'English'), ('FR', 'Francais')), default='EN')

    def __str__(self):
        return self.user.__str__() + self.preferred_language


class Auction(models.Model):
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    minimum_price = models.DecimalField(max_digits=11, decimal_places=2)
    current_price = models.DecimalField(max_digits=11, decimal_places=2)
    deadline = models.DateTimeField(default=datetime.datetime.today()+datetime.timedelta(minutes=1)) #TODO : timedelta(days=3)
    status = models.CharField(max_length=2,
                              choices=(('AC', 'Active'), ('BA', 'Banned'), ('DU', 'DUE'), ('AD', 'Adjudicated')),
                              default='AC')
    seller = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=1, related_name='seller')
    last_bidder = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='last_bidder', null=True)


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='bidder', null=False)
    auction = models.ForeignKey(Auction, on_delete=models.DO_NOTHING, related_name='auction', null=False)
    bid_price = models.DecimalField(max_digits=11, decimal_places=2)