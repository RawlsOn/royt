from rest_framework import generics, status
from rest_framework.response import Response

from . import jwt_serializers

from rest_framework_simplejwt.views import TokenViewBase

class TokenObtainPairView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = jwt_serializers.TokenObtainPairSerializer


token_obtain_pair = TokenObtainPairView.as_view()


class TokenRefreshView(TokenViewBase):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """
    serializer_class = jwt_serializers.TokenRefreshSerializer


token_refresh = TokenRefreshView.as_view()
