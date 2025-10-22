from django.conf import settings

from common.util.romsg import rp
import subprocess
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone as django_timezone
from pytz import timezone
from django.db.models import QuerySet

import common.util.datetime_util as dt_util
import common.util.str_util as str_util
from common.util.logger import RoLogger
logger = RoLogger()
from argparse import Namespace
from common.util import curlreq
import rawarticle.models as rawarticle_models
import core.models as core_models
import monitoring.models as m_models
from common.util.AwsUtil import AwsUtil
from django.apps import apps
# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# ./manage.py run_job_monitor --run_type=proto
# ./manage.py run_job_monitor --run_type=default

TODAY = django_timezone.now().date()

class JobMonitor(object):

    def __init__(self, args={}):
        self.args = args

    def run_proto(self):
        print('run JobMonitor Proto')
        self.stat = {}
        self.count_proto_article_created_today()
        pp.pprint(self.stat)
        m_models.ArticleProto.objects.create(**self.stat)

    def run(self):
        print('run JobMonitor Article')
        self.stat = {}
        SIDOS = settings.REGION_TARGETS
        SIDOS = ['경기도']
        for sido in SIDOS:
            self.count_sido(sido)
        pp.pprint(self.stat)
        m_models.Article.objects.create(**self.stat)

    def count_proto_article_created_today(self):
        rp('counting proto_article_created_today')
        created_today = rawarticle_models.ProtoArticle.objects.filter(
            created_date=TODAY
        )
        self.stat['proto_article_created_today'] = created_today.count()

        rp('counting proto_article_processed_today')
        processed_today = created_today.filter(
            is_processed= True
        )
        self.stat['proto_article_processed_today'] = processed_today.count()

    def count_sido(self, sido):
        rp('counting ' + sido + '_created_today')
        model = apps.get_model('core', 'Article' + sido)

        total = model.objects.all()
        self.stat[sido + '_total'] = total.count()

        # created_today = model.objects.filter(
        #     created_date=TODAY
        # )
        # self.stat[sido + '_created_today'] = created_today.count()

        # rp('counting ' + sido + '_updated_today')
        # updated_today = model.objects.filter(
        #     updated_at__gte=TODAY
        # )
        # self.stat[sido + '_updated_today'] = updated_today.count()

        rp('counting ' + sido + '_has_detail')
        has_detail = model.objects.filter(
            has_detail_text= True
        )
        self.stat[sido + '_has_detail'] = has_detail.count()

        # stat = m_models.Article.objects.last().__dict__
        # last = stat[sido + '_has_detail']
        # if last is None:
        #     last = 0
        # has_detail_gap = self.stat[sido + '_has_detail'] - last
        # self.stat[sido + '_has_detail_gap'] = has_detail_gap

        # rp('counting ' + sido + '_is_detail_processed')
        # is_detail_processed = has_detail.filter(
        #     is_detail_processed= True
        # )
        # self.stat[sido + '_is_detail_processed'] = is_detail_processed.count()

        # rp('counting ' + sido + '_is_detail_failed')
        # is_detail_failed = has_detail.filter(
        #     is_detail_failed= True
        # )
        # self.stat[sido + '_is_detail_failed'] = is_detail_failed.count()

        # rp('counting ' + sido + '_is_pnu_processed')
        # is_pnu_processed = has_detail.filter(
        #     pnu_processed_at__isnull= False
        # )
        # self.stat[sido + '_is_pnu_processed'] = is_pnu_processed.count()

        rp('counting ' + sido + '_is_pnu_null')
        is_pnu_null = has_detail.filter(
            is_detail_failed= False,
            pnu__isnull= True
        )
        self.stat[sido + '_is_pnu_null'] = is_pnu_null.count()
