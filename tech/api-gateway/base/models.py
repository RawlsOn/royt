import pprint
import glob
import os
import time
import io
from datetime import datetime, date, timedelta
import base.models as base_models
from django.conf import settings
from django.db import models
from itertools import chain
from django.utils import timezone
import uuid

def to_dict(instance):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields):
        data[f.name] = f.value_from_object(instance)
        # date to string
        if str(type(data[f.name])) == "<class 'datetime.date'>":
            data[f.name] = data[f.name].strftime('%Y-%m-%d')
        # decimal to string
        if str(type(data[f.name])) == "<class 'decimal.Decimal'>":
            data[f.name] = str(data[f.name])
        if isinstance(data[f.name], float):
            data[f.name] = str(data[f.name])
    # for f in opts.many_to_many:
    #     data[f.name] = [i.id for i in f.value_from_object(instance)]
    return data

class RoBase(models.Model):

    created_date = models.DateField(auto_now_add=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract= True
        # first로 얻을 때 가장 오래된 것이 나옴
        ordering = ('created_at', )

    @property
    def to_obj(self):
        dict_obj = to_dict(self)
        return dict_obj

class LogBase(models.Model):

    created_date = models.DateField(auto_now_add=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    job_id = models.IntegerField(db_index=True)
    tag = models.CharField(max_length=16, db_index=True)

    is_success = models.BooleanField(default=False)

    text = models.TextField()

    class Meta:
        abstract= True
        # first로 얻을 때 가장 오래된 것이 나옴
        ordering = ('created_at', )

    @property
    def to_obj(self):
        dict_obj = to_dict(self)
        return dict_obj

class FrontendVersion(base_models.RoBase):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    note = models.CharField(max_length=255, db_index=True, blank=True)

    class Meta:
        # first로 얻을 때 가장 최근 것이 나옴
        ordering = ('-created_at', )

###########
## Chory
###########

class Chory(base_models.RoBase):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    owner_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    # 화면표시용. content로부터 자동 생성
    rep_content = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract= True
        # first로 얻을 때 가장 최근 것이 나옴
        ordering = ('-created_at', )

class Comment(base_models.RoBase):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    parent_id = models.UUIDField(db_index=True)
    # VoteChory, WeChory, VoteComment, WeComment 등
    parent_type = models.CharField(max_length=16, db_index=True)
    owner_id = models.UUIDField(db_index=True)
    content = models.TextField(null=True, blank=True)
    rep_content = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract= True
        # first로 얻을 때 가장 최근 것이 나옴
        ordering = ('-created_at', )

class Like(base_models.RoBase):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    owner_id = models.UUIDField(db_index=True)
    # VoteChory, WeChory, VoteComment, WeComment 등
    parent_type = models.CharField(max_length=16, db_index=True)
    parent_id = models.UUIDField(db_index=True)

    class Meta:
        abstract= True
        # first로 얻을 때 가장 최근 것이 나옴
        ordering = ('-created_at', )