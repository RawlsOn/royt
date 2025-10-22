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

from rticler.models.article import Article
from rticler.models.article import TempArticle

# ./manage.py test user.tests.test_base

class BaseArticleTestCase(TestCase):
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

    def test_비로그인시_아티클_생성_실패(self):
        resp = self.client.post('/api/rticler/article/', {
            'title': 'title',
            'content': 'content',
        })
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_아티클_생성(self):
        resp = self.client.post('/api/user/token/', {
            'email': self.a_email,
            'password': self.a_password
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data['access'])

        resp = self.client.post('/api/rticler/article/', {
            'title': 'title',
            'content': 'content',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_임시저장후_아티클_생성(self):
        self.client.force_authenticate(user= self.a_user)
        resp = self.client.post('/api/rticler/temp-article/', {
            'title': 'title',
            'content': 'content',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # 임시저장은 계속 업데이트됨
        temp_article_id = resp.data['id']
        resp = self.client.patch(f"/api/rticler/temp-article/{temp_article_id}/", {
            'title': 'title',
            'content': 'content updated',
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['content'], 'content updated')
        self.assertEqual(resp.data['user'], self.a_user.pk)

        self.assertEqual(TempArticle.objects.count(), 1)

        # 아티클 생성
        resp = self.client.post('/api/rticler/article/', {
            'title': 'title',
            'content': 'content',
            'temp_article': temp_article_id
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['content'], 'content')

    def test_다른_사람이_수정_또는_삭제_못함(self):
        self.client.force_authenticate(user= self.a_user)
        resp = self.client.post('/api/rticler/article/', {
            'title': 'title',
            'content': 'content',
        })
        article_id = resp.data['id']

        self.client.force_authenticate(user= self.b_user)
        resp = self.client.patch(f"/api/rticler/article/{article_id}/", {
            'title': 'title',
            'content': 'content updated',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = self.client.delete(f"/api/rticler/article/{article_id}/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_남의_아티클을_볼_수_있음(self):
        self.client.force_authenticate(user= self.a_user)
        resp = self.client.post('/api/rticler/article/', {
            'title': 'A title',
            'content': 'A content',
        })

        self.client.force_authenticate(user= self.b_user)
        resp = self.client.post('/api/rticler/article/', {
            'title': 'B title',
            'content': 'B content',
        })

        resp = self.client.get('/api/rticler/article/')
        self.assertEqual(resp.data['count'], 2)

    def test_남의_임시_아티클은_볼_수_없음(self):
        self.client.force_authenticate(user= self.a_user)
        resp = self.client.post('/api/rticler/temp-article/', {
            'title': 'A title',
            'content': 'A content',
        })

        self.client.force_authenticate(user= self.b_user)
        resp = self.client.post('/api/rticler/temp-article/', {
            'title': 'B title',
            'content': 'B content',
        })

        resp = self.client.get('/api/rticler/temp-article/')
        self.assertEqual(resp.data['count'], 1)

    def test_비로그인시에도_아티클을_볼_수_있음(self):
        Article.objects.create(
            user= self.a_user,
            title= 'title 1'
        )
        Article.objects.create(
            user= self.a_user,
            title= 'title 2'
        )

        resp = self.client.get('/api/rticler/article/')
        self.assertEqual(resp.data['count'], 2)


    def test_남의_아티클을_수정할_수_없음(self):
        self.client.force_authenticate(user= self.a_user)
        # 아티클 생성
        resp = self.client.post('/api/rticler/article/', {
            'title': 'title',
            'content': 'content',
        })
        article_pk = resp.data['id']

        # 내 아티클은 수정가능
        resp = self.client.patch(f"/api/rticler/article/{article_pk}/", {
            'title': 'title',
            'content': 'content updated',
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['content'], 'content updated')

        self.client.force_authenticate(user= self.b_user)
        # 남의 아티클은 수정불가
        resp = self.client.patch(f"/api/rticler/article/{article_pk}/", {
            'title': 'title',
            'content': 'content updated',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_남의_아티클을_삭제할_수_없음(self):
        self.client.force_authenticate(user= self.a_user)
        # 아티클 생성
        resp = self.client.post('/api/rticler/article/', {
            'title': 'title',
            'content': 'content',
        })
        article_pk = resp.data['id']

        self.client.force_authenticate(user= self.b_user)
        # 남의 아티클은 삭제불가
        resp = self.client.delete(f"/api/rticler/article/{article_pk}/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.force_authenticate(user= self.a_user)
        # 내 아티클은 삭제가능
        resp = self.client.delete(f"/api/rticler/article/{article_pk}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)



        # # with open("./resources/federer.png", 'rb') as fp:
        # response = self.client.post('/api/계약/', {
        #     '임대물건': userA_임대물건.pk,
        #     '임차인': userA_임차인.pk,

        #     '계약시작일': '2022-02-02',
        #     '계약종료일': '2023-02-01'
        #     # '계약서_사진_1': fp
        # }, format= 'multipart')
        #     # print(response.data)
