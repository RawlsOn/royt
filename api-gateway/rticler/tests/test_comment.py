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

from rticler.models.comment import Comment

# ./manage.py test rticler.tests.test_comment

class BaseCommentTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.a_email = 'a@a.com'
        self.a_password = 'password'
        self.a_user = CustomUser.objects.create_user(
            self.a_email,
            self.a_password
        )

        self.b_email = 'b@b.com'
        self.b_password = 'password'
        self.b_user = CustomUser.objects.create_user(
            self.b_email,
            self.b_password
        )

    def base_auth(self):
        self.assertEqual(True, True)

    def test_비로그인시_코멘트_생성_실패(self):
        resp = self.client.post('/api/rticler/comment/', {
            'title': 'title',
            'content': 'content',
        })
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_코멘트_생성(self):
        resp = self.client.post('/api/user/token/', {
            'email': self.a_email,
            'password': self.a_password
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data['access'])

        resp = self.client.post('/api/rticler/comment/', {
            'title': 'title',
            'content': 'content',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_다른_사람이_수정_또는_삭제_못함(self):
        self.client.force_authenticate(user= self.a_user)
        resp = self.client.post('/api/rticler/comment/', {
            'title': 'title',
            'content': 'content',
        })
        article_id = resp.data['id']

        self.client.force_authenticate(user= self.b_user)
        resp = self.client.patch(f"/api/rticler/comment/{article_id}/", {
            'title': 'title',
            'content': 'content updated',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = self.client.delete(f"/api/rticler/comment/{article_id}/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_비로그인시에도_코멘트를_볼_수_있음(self):

        Comment.objects.create(
            user= self.a_user,
            title= 'title 1'
        )
        Comment.objects.create(
            user= self.a_user,
            title= 'title 2'
        )

        resp = self.client.get('/api/rticler/comment/')
        self.assertEqual(resp.data['count'], 2)
