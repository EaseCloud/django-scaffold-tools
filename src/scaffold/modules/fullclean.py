""" Automated call full_clean method on each model instance save """
from django.contrib.sessions.models import Session
from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save)
def pre_save_full_clean_handler(sender, instance):
    """ Force all models to call full_clean before save """
    if sender != Session:
        instance.full_clean()
