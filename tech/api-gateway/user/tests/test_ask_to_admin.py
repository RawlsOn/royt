import os
from user.models import CustomUser
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
import common.util.model_util as model_util
import common.util.datetime_util as datetime_util

from django.utils.timezone import make_aware
from django.utils import timezone


# ./manage.py test user.tests.test_ask_to_admin

class AskToAdminTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.a_email = 'a@a.com'
        self.a_password = 'password'

        self.a_user = CustomUser.objects.create_user(
            self.a_email,
            self.a_password
        )

    def test_base(self):
        self.client.force_authenticate(user= self.a_user)

        resp = self.client.post('/api/user/ask-to-admin/', {
            'content': 'content',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.get('/api/user/ask-to-admin/')
        self.assertEqual(resp.data['count'], 1)
