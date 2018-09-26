import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    preferred_language = models.CharField(max_length=2, choices=(('EN', 'English'), ('FR', 'Francais')), default='EN')

    def __str__(self):
        return self.user.__str__() + self.preferred_language


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Auction(models.Model):
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    minimum_price = models.FloatField()
    deadline = models.DateTimeField(default=datetime.datetime.today()+datetime.timedelta(days=1))
    status = models.CharField(max_length=2,
                              choices=(('AC', 'Active'), ('BA', 'Banned'), ('DU', 'DUE'), ('AD', 'Adjudicated')),
                              default='AC')
    seller = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=1)
