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

import main.models as main_models

# ./manage.py test main.tests.test_base_filter --keepdb

class BaseFilterTestCase(TestCase):
    databases = '__all__'

    def setUp(self):
        self.client = APIClient()

    def test_model(self):
        self.assertEqual(main_models.토지.objects.all().count(), 19)
        self.assertEqual(main_models.토지매물.objects.all().count(), 19)
        self.assertEqual(main_models.토지매물노트.objects.all().count(), 13)

        self.assertEqual(main_models.건물.objects.all().count(), 94)
        self.assertEqual(main_models.건물매물.objects.all().count(), 98)
        self.assertEqual(main_models.건물매물노트.objects.all().count(), 28)

        self.assertEqual(main_models.상가.objects.all().count(), 134)
        self.assertEqual(main_models.상가매물.objects.all().count(), 135)
        self.assertEqual(main_models.상가매물노트.objects.all().count(), 43)

    def test_정상_api(self):
        resp = self.client.get('/api/main/토지매물/?토지__geo_unit_id__in=24,56,136,137,235,236', {
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 3)

    def test_평당가격_lte_70000000_api(self):
        resp = self.client.get('/api/main/토지매물/?토지__geo_unit_id__in=24,56,136,137,235,236&평당가격__lte=70000000', {
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 2)

    def test_토지__지목_2종일반주거_api(self):
        resp = self.client.get('/api/main/토지매물/?토지__geo_unit_id__in=24,56,136,137,235,236&토지__용도지역__in=2종일반주거', {
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 2)

    def test_토지__지목_2종일반주거_3종일반주거_api(self):
        resp = self.client.get('/api/main/토지매물/?토지__geo_unit_id__in=24,56,136,137,235,236&토지__용도지역__in=2종일반주거,3종일반주거', {
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 3)

    def test_건물매물_api(self):
        건물있는_geo_unit_ids = ','.join([str(x.geo_unit_id) for x in main_models.건물.objects.all()])
        resp = self.client.get(f'/api/main/건물매물/?건물__geo_unit_id__in={건물있는_geo_unit_ids}', {
        })
        self.assertEqual(resp.data['count'], 98)

        resp = self.client.get(f'/api/main/건물매물/?건물__geo_unit_id__in={건물있는_geo_unit_ids}&건물__준공년도__gte=2001', {
        })
        self.assertEqual(resp.data['count'], 32)

        resp = self.client.get(f'/api/main/건물매물/?건물__geo_unit_id__in={건물있는_geo_unit_ids}&건물__준공년도__lte=2000', {
        })
        self.assertEqual(resp.data['count'], 64)

        resp = self.client.get(f'/api/main/건물매물/?건물__geo_unit_id__in={건물있는_geo_unit_ids}&건물__준공년도__isnull=True', {
        })
        self.assertEqual(resp.data['count'], 2)