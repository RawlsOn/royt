import os
from user.models import CustomUser
import json


from rest_framework.test import APIRequestFactory, APIClient
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

from tenniscode.models import Club

# ./manage.py test tenniscode.tests.test_club_comment

class BaseCommentTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.club_ltc = Club.objects.create(
            title= 'LTC',
            기준일= timezone.now()
        )

    def test_base_auth(self):
        self.assertEqual(True, True)

    def test_base_comment(self):
        resp = self.client.get(f"/api/club/{self.club_ltc.id}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['comments']), 0)

        resp = self.client.post(f"/api/club/{self.club_ltc.id}/anon-comment/", {
            'content': 'content',
            'writer_name': 'federer',
            'writer_pw': 'haha1234'
        })
        comment_id = resp.data['comment']['id']
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.get(f"/api/club/{self.club_ltc.id}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['comments']), 1)

        resp = self.client.delete(f"/api/club/{self.club_ltc.id}/anon-comment/{comment_id}/", {
            'writer_pw': 'wrong-pw'
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = self.client.get(f"/api/club/{self.club_ltc.id}/")
        self.assertEqual(len(resp.data['comments']), 1)

        resp = self.client.delete(f"/api/club/{self.club_ltc.id}/anon-comment/{comment_id}/", {
            'writer_pw': 'haha1234'
        })
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        resp = self.client.get(f"/api/club/{self.club_ltc.id}/")
        self.assertEqual(len(resp.data['comments']), 0)

    def test_parent_child(self):
        resp = self.client.get(f"/api/club/{self.club_ltc.id}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['comments']), 0)

        resp = self.client.post(f"/api/club/{self.club_ltc.id}/anon-comment/", {
            'content': 'content - i am parent',
            'writer_name': 'federer',
            'writer_pw': 'haha1234'
        })
        parent_comment_id = resp.data['comment']['id']
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.post(f"/api/club/{self.club_ltc.id}/anon-comment/", {
            'parent': parent_comment_id,
            'content': 'content - i am children',
            'writer_name': 'federer',
            'writer_pw': 'haha1234'
        })

        resp = self.client.post(f"/api/club/{self.club_ltc.id}/anon-comment/", {
            'parent': parent_comment_id,
            'content': 'content - i am children 2',
            'writer_name': 'federer',
            'writer_pw': 'haha1234'
        })

        resp = self.client.get(f"/api/club/{self.club_ltc.id}/")
        # parent가 있는 것은 안 나옴
        self.assertEqual(len(resp.data['comments']), 1)

        parent = resp.data['comments'][0]
        self.assertEqual(len(parent['children']), 2)
