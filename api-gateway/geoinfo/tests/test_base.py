import os
import json

from rest_framework.test import APIRequestFactory, force_authenticate, APIClient
from rest_framework import status
from django.test import TestCase
from dateutil.relativedelta import relativedelta

import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

from argparse import Namespace

from datetime import datetime, date, timedelta

import rest_framework.status
from django.utils import timezone

import geoinfo.models as geoinfo_models

# ./manage.py test geoinfo.tests.test_base --keepdb

class BaseFilterTestCase(TestCase):
    databases = '__all__'

    def setUp(self):
        self.client = APIClient()

    def test_model(self):
        self.assertEqual(geoinfo_models.GeoUnit.objects.all().count(), 240)
        geoinfo_models.GeoUnit.objects.first().delete()
        self.assertEqual(geoinfo_models.GeoUnit.objects.all().count(), 239)

    def test_model_2(self):
        self.assertEqual(geoinfo_models.GeoUnit.objects.all().count(), 240)
        geoinfo_models.GeoUnit.objects.first().delete()
        self.assertEqual(geoinfo_models.GeoUnit.objects.all().count(), 239)