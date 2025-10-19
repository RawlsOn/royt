import urllib
from common.util import api_util
from common.util.logger import RoLogger
import rest_framework
from rest_framework.views import APIView
from rest_framework import status, filters, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
import io
import time
import os
import glob
import pprint
import json
import re
import shutil
import ntpath
import sys
import csv
pp = pprint.PrettyPrinter(indent=2)  # pp.pprint()
logger = RoLogger()

import base.models as base_models
import base.serializers as base_serializers

class Log4j(generics.ListCreateAPIView):
    permission_classes = [rest_framework.permissions.AllowAny]
    allowed_methods = ('POST',)
    serializer_class = rest_framework.serializers.Serializer
    def post(self, request, format=None):
        logger.INFO('Log4j', request=request)
        return Response(
            status=status.HTTP_200_OK
        )

class GetFrontendVersion(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = base_serializers.FrontendVersionSerializer
    allowed_methods = ('GET',)
    queryset = base_models.FrontendVersion.objects.all()[:1]
