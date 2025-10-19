from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db import models
import base.models as base_models
# from django.contrib.gis.db import models as gis_models

import uuid
from django.db.models.signals import post_save

import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
from common.util import juso_util, model_util, str_util, geo_util, datetime_util
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()


# rm /usr/data/tojimetriclocal/roemail_db.sqlite3;
# rm roemail/migrations/00*
# ./manage.py makemigrations roemail
# ./manage.py migrate roemail --database=roemail

from django.db import models

class SendJob(base_models.RoBase):

    to = models.EmailField(verbose_name='수신자')

    subject = models.CharField(max_length=255, verbose_name='제목')

    # plain or html
    content_type = models.CharField(max_length=8, default='plain')
    # async, sync: sync는 그냥 바로 보냄. 여기에는 기록용으로 남김
    send_type = models.CharField(max_length=8, default='async')
    content = models.TextField()

class SendLog(base_models.LogBase):
    pass

class Invitation(base_models.RoBase):
    invitator = models.UUIDField()
    invitee_email = models.EmailField()

class EmailLoginjoinCode(base_models.RoBase):
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6, db_index=True)

    loginjoin_at = models.DateTimeField(null=True, db_index=True)

