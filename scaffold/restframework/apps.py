""" DRF extensions modules to be integrated together """
from django.apps import AppConfig


class MetaConfig(AppConfig):
    """ AppConfig for the module """
    name = 'scaffold.restframework'
