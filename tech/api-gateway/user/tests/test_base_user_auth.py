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


# ./manage.py test user.tests.test_base_user_auth

class BaseUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.a_email = 'a@a.com'
        self.a_password = 'password'

        self.a_user = CustomUser.objects.create_user(
            self.a_email,
            self.a_password
        )

    def base_auth(self):
        self.assertEqual(True, True)

    def test_join(self):
        resp = self.client.post('/api/user/join/', {
            'email': self.a_email,
            'password': self.a_password
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(str(resp.data['email'][0]), '사용자의 email은/는 이미 존재합니다.')
        self.assertEqual(str(resp.data['email'][0]), 'user with this email already exists.')

        resp = self.client.post('/api/user/join/', {
            'email': 'federer@tennis.com',
            'password': 'federer'
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data['access'])
        resp = self.client.get('/api/user/get-user/' + str(resp.data['user_id']) + '/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_login(self):
        resp = self.client.get('/api/user/get-user/' + str(self.a_user.id) + '/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        resp = self.client.post('/api/user/token/', {
            'email': self.a_email,
            'password': self.a_password
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data['access'])
        resp = self.client.get('/api/user/get-user/' + str(self.a_user.id) + '/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.assertEqual(resp.data['email'], self.a_email)

    def test_login_fail(self):
        resp = self.client.post('/api/user/token/', {
            'email': 'bad-email',
            'password': self.a_password
        })
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password(self):
        resp = self.client.post('/api/user/token/', {
            'email': self.a_email,
            'password': self.a_password
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data['access'])
        resp = self.client.get('/api/user/get-user/' + str(self.a_user.id) + '/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        new_pw = 'newpwhaha'
        resp = self.client.patch('/api/user/change-password/', {
            'password': 'wrong-password',
            'password_to_change': new_pw
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = self.client.patch('/api/user/change-password/', {
            'password': self.a_password,
            'password_to_change': new_pw
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.client.post('/api/user/token/', {
            'email': self.a_email,
            'password': new_pw
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_forgot_password(self):

        resp = self.client.get('/api/user/forgot-password/', {
            'email': 'bad-email'
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = self.client.get('/api/user/forgot-password/', {
            'email': self.a_email
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # 기존 비번으로 로그인 불가
        resp = self.client.post('/api/user/token/', {
            'email': self.a_email,
            'password': self.a_password
        })
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


