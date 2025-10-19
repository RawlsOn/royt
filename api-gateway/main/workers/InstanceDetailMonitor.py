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
from django.apps import apps
from common.util.AwsUtil import AwsUtil
# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# ./manage.py run_article_collector
# /home/admin/Works/mkay/onenlc/api-gateway/venv/bin/python /home/admin/Works/mkay/onenlc/api-gateway/manage.py run_article_collector
# ssh -i ~/.ssh/aws-ro-seoul.pem -o ServerAliveINterval=10 ec2-user@3.39.230.17

class InstanceDetailMonitor(object):

    def __init__(self, args={}):
        self.args = args
        self.sidos = settings.REGION_TARGETS
        # self.aws_util = AwsUtil()

    def _total_count(self):
        self.total_count = {}
        for sido in self.sidos:
            model = apps.get_model('core', 'Article' + sido)
            self.total_count[sido] = model.objects.filter(
                has_history= False,
                created_at__gte=django_timezone.now().date()
            ).count()

    def run(self):
        print('run InstanceDetailMonitor')
        # self.restore_default_setting()
        while True:
            try:
                self.watch_article_detail_colection()
                print('InstanceDetailMonitor: Sleeping for 97 seconds...')
                time.sleep(97)
            except Exception    as e:
                rp(str(e), msg_type='NOTICE')
                raise e

    def watch_article_detail_colection(self):
        rp('querying total count...')
        self._total_count()
        self.done_count = {}
        result = []
        rp('querying done count...')
        for sido in self.sidos:
            model = apps.get_model('core', 'Article' + sido)
            count = model.objects.filter(
                has_detail_text= True,
                has_history= False,
                created_at__gte=django_timezone.now().date()
            ).count()
            result.append(' '.join([
                sido,
                str(int(count / self.total_count[sido] * 100)) + '%',
                str(count), ' / ',
                str(self.total_count[sido]),
            ]))

        rp('\n' + '\n'.join(result), msg_type='NOTICE')

    def restore_default_setting(self):
        default = rawarticle_models.ArticleDetailCollectorTargetCount.objects.first().__dict__
        del default['_state']
        rawarticle_models.ArticleDetailCollectorTargetCount.objects.all().delete()
        rawarticle_models.ArticleDetailCollectorTargetCount.objects.create(
            **default
        )

def t(unberbar):
    return unberbar.replace('_', '-')