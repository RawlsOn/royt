from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db import models
import base.models as base_models
import uuid
from django.db.models.signals import post_save

import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

import user.models as user_models

# ./manage.py makemigrations monitoring
# ./manage.py migrate monitoring --database=monitoring

class ArticleProto(base_models.RoBase):
    proto_article_created_today = models.PositiveIntegerField(blank=True, null=True)
    proto_article_processed_today = models.PositiveIntegerField(blank=True, null=True)

class Article(base_models.RoBase):
    서울시_total = models.PositiveIntegerField(blank=True, null=True)
    서울시_created_today = models.PositiveIntegerField(blank=True, null=True)
    서울시_updated_today = models.PositiveIntegerField(blank=True, null=True)
    서울시_has_detail = models.PositiveIntegerField(blank=True, null=True)
    서울시_has_detail_gap = models.PositiveIntegerField(blank=True, null=True)
    서울시_has_detail_created_today = models.PositiveIntegerField(blank=True, null=True)
    서울시_NOT_has_detail_created_today = models.PositiveIntegerField(blank=True, null=True)
    서울시_is_detail_processed = models.PositiveIntegerField(blank=True, null=True)
    서울시_is_detail_failed = models.PositiveIntegerField(blank=True, null=True)
    서울시_is_pnu_processed = models.PositiveIntegerField(blank=True, null=True)
    서울시_is_pnu_null = models.PositiveIntegerField(blank=True, null=True)

    경기도_total = models.PositiveIntegerField(blank=True, null=True)
    경기도_created_today = models.PositiveIntegerField(blank=True, null=True)
    경기도_updated_today = models.PositiveIntegerField(blank=True, null=True)
    경기도_has_detail = models.PositiveIntegerField(blank=True, null=True)
    경기도_has_detail_gap = models.PositiveIntegerField(blank=True, null=True)
    경기도_has_detail_created_today = models.PositiveIntegerField(blank=True, null=True)
    경기도_NOT_has_detail_created_today = models.PositiveIntegerField(blank=True, null=True)
    경기도_is_detail_processed = models.PositiveIntegerField(blank=True, null=True)
    경기도_is_detail_failed = models.PositiveIntegerField(blank=True, null=True)
    경기도_is_pnu_processed = models.PositiveIntegerField(blank=True, null=True)
    경기도_is_pnu_null = models.PositiveIntegerField(blank=True, null=True)

    인천시_total = models.PositiveIntegerField(blank=True, null=True)
    인천시_created_today = models.PositiveIntegerField(blank=True, null=True)
    인천시_updated_today = models.PositiveIntegerField(blank=True, null=True)
    인천시_has_detail = models.PositiveIntegerField(blank=True, null=True)
    인천시_has_detail_gap = models.PositiveIntegerField(blank=True, null=True)
    인천시_has_detail_created_today = models.PositiveIntegerField(blank=True, null=True)
    인천시_NOT_has_detail_created_today = models.PositiveIntegerField(blank=True, null=True)
    인천시_is_detail_processed = models.PositiveIntegerField(blank=True, null=True)
    인천시_is_detail_failed = models.PositiveIntegerField(blank=True, null=True)
    인천시_is_pnu_processed = models.PositiveIntegerField(blank=True, null=True)
    인천시_is_pnu_null = models.PositiveIntegerField(blank=True, null=True)