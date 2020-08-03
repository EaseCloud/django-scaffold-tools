""" Extended rest_framework authentication classes """
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """ Replacing the Csrf Authentication """

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
