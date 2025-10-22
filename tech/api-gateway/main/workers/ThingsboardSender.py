from django.conf import settings
from common.util.romsg import rp

import io, time, os, glob, pprint, json, re, shutil, ntpath, csv, random
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models import QuerySet
import common.util.datetime_util as dt_util
from common.util import curlreq

import common.util.datetime_util as datetime_util
import common.util.str_util as str_util
from common.util.logger import RoLogger
logger = RoLogger()
from argparse import Namespace
from random import randint
from django.apps import apps
import rawarticle.models as rawarticle_models
from common.util import tb_util
from common.util.ThingsboardUtil import ThingsboardUtil
from main.workers.InstanceMonitor import InstanceMonitor
from main.workers.DailyStatMaker import DailyStatMaker

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# ./manage.py run_article_detail_collector

class ThingsboardSender(object):

    def __init__(self, args={}):
        self.args = args
        self.sidos = ['서울시', '경기도']
        self.instance_watcher_tb = ThingsboardUtil(self.args)
        self.instance_watcher_tb.device_token = 'fnqehXmSjTCUAbhK1Agi'
        self.job_watcher_tb = ThingsboardUtil(self.args)
        self.job_watcher_tb.device_token = 'IbYpdrshEt8hlhvyoRo9'
        self.instance_monitor = InstanceMonitor(self.args)

    def run(self):
        print('run ThingsboardSender', self.args)

        if self.args.interval == 10:
            while True:
                try:
                    self.send_proto_article_count()
                    self.send_core_article_count()
                    self.send_daily_job_done()
                    # self.send_instance_count()
                    rp('ThingsboardSender: Sleeping for 10 minutes...')
                    time.sleep(600)
                except Exception as e:
                    if 'Lost connection to server during query' in str(e) or 'Server has gone away' in str(e):
                        rp('Lost connection to server during query. Wait for 60 seconds.')
                        time.sleep(60)
                        return
                    raise e

        # self.send_instance_count()

    def send_instance_count(self):
        result = self.instance_monitor.get_instance_stat_count()
        self.instance_watcher_tb.send(result)

    def send_proto_article_count(self):
        count_map = {}
        count_map['ProtoArticle'] =  rawarticle_models.ProtoArticle.objects.count()
        count_map['ProtoArticleProcessed'] =  rawarticle_models.ProtoArticle.objects.filter(is_processed=True).count()
        self.job_watcher_tb.send(count_map)

    def send_core_article_count(self):
        for sido in self.sidos:
            model = apps.get_model('core', 'Article' + sido)
            count_map = {}
            count_map['CoreArticle' + sido] =  model.objects.count()
            count_map['CoreArticle' + sido + 'DetailProcessed'] =  model.objects.filter(is_detail_processed=True).count()
            count_map['CoreArticle' + sido + 'DetailFailed'] =  model.objects.filter(is_detail_failed=True).count()
            self.job_watcher_tb.send(count_map)

    def send_daily_job_done(self):
        ret_map = {}
        today = rawarticle_models.ProtoArticle.objects.filter(
            created_date=timezone.now().date()
        )
        today_done = today.filter(
            is_processed=True
        )
        ret_map['Article'] = today.count() == today_done.count()

        is_daily_stat_maker_runnable = True

        for sido in self.sidos:
            model = apps.get_model('core', 'Article' + sido)
            today = model.objects.filter(
                created_date=timezone.now().date()
            ).count()
            today_done = model.objects.filter(
                created_date=timezone.now().date(),
                is_detail_processed=True
            ).count()
            today_failed = model.objects.filter(
                created_date=timezone.now().date(),
                is_detail_failed=True
            ).count()
            ret_map['Detail' + sido] = today == today_done + today_failed
            is_daily_stat_maker_runnable = is_daily_stat_maker_runnable and ret_map['Detail' + sido]

        daily_stat_maker_result = ''
        if is_daily_stat_maker_runnable:
            self.args.today = timezone.now().date()
            daily_stat_maker_result = DailyStatMaker(self.args).run(sido)

        self.job_watcher_tb.send(ret_map)
        self.job_watcher_tb.send(daily_stat_maker_result)