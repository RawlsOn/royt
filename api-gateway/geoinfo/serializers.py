from cmath import log
import logging
from urllib.parse import urlencode
import requests
import slack_sdk
from django.db.models import Sum
from django.db.models.functions import Coalesce
from slack_sdk.errors import SlackApiError
from traceback import print_exc
import json

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from django.conf import settings
from django.contrib import auth
from django.shortcuts import redirect
from rest_framework import serializers, viewsets, mixins, generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
from django.utils import timezone
from functools import reduce

from datetime import datetime

import geoinfo.models as geoinfo_models

import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

class GeoUnitSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(GeoUnitSerializer, self).__init__(*args, **kwargs)

        print('__init___')


    center_x = serializers.ReadOnlyField()
    center_y = serializers.ReadOnlyField()

    class Meta:
        model = geoinfo_models.GeoUnit
        fields = '__all__'
