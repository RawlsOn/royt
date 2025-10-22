from django.conf import settings

from common.util.romsg import rp as romsg_rp
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
from bs4 import BeautifulSoup
from django.apps import apps
from random import randint
import core.models as core_models
import rawarticle.models as rawarticle_models
# from main.workers.ArticleHtmlGetter import ArticleHtmlGetter

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# ./manage.py run_article_detail_collector
# 도커 안에서는 못 돌림

TODAY = timezone.now().date()
# TODAY = '2023-08-12'

def rp(text, msg_type='INFO', filename='romsg', raise_error=False):
    romsg_rp(
        '(detail)' + text,
        msg_type,
        filename='romsg_article_detail_collector',
        raise_error= raise_error
    )

class ArticleDetailCollector(object):

    def __init__(self, args={}):
        self.args = args
        self.sidos = settings.REGION_TARGETS

    def run(self):
        print('run ArticleDetailCollector', self.args)
        if self.args.sido is not None:
            self._run(self.args.sido)
        else:
        # rp('not running detail collector')
        # time.sleep(60 * 60 * 24 * 7)
            random.shuffle(self.sidos)
            self._run(self.sidos[0])

    def get_total_count(self):
        rp('query total count...')
        total_count = 0
        for sido in settings.REGION_TARGETS:
            model = apps.get_model('core', 'Article' + sido)
            total_count += model.objects.filter(
                has_detail_text= False,
                has_history= False
            ).count()
        return total_count

    def _run(self, sido):
        model = apps.get_model('core', 'Article' + sido)
        while True:
        # parser = Parser(self.args)
        # self.parser = Parser(self.args)
        # self.post_parser = PostParser(self.args)

            print(sido + 'raw quering...')
            # targets = model.objects.filter(
            #     has_detail_text= False
            # )
            QUERY = f"""
SELECT * FROM core_article{sido}
WHERE has_detail_text= 0 and is_detail_processed= 0 and is_detail_failed= 0
LIMIT 10
OFFSET {self.args.no}
            """
            print(QUERY)
            try:
                targets = model.objects.raw(QUERY)
                rp('length ' + str(len(targets)))
                if len(targets) == 0:
                    rp('DONE. Wait 10 min')
                    time.sleep(60 * 10)
                    continue

                for target in targets:
                    rp('OFFSET: ' + str(self.args.no))
                    if target is None:
                        rp('target is None, DONE')
                        raise Exception('FINISHED')
                        return
                    self.process(target)

            except Exception as e:
                if 'Lost connection to server during query' in str(e):
                    rp('Lost connection to server during query. Stop. wait 1 min')
                    time.sleep(60)
                    return

                if 'Server has gone away' in str(e):
                    rp('Server has gone away. Stop. wait 1 min')
                    time.sleep(60)
                    return

                if 'FINISHED' in str(e):
                    rp('FINISHED, wait 1 min')
                    time.sleep(60 * 1)
                    return

                error_str = str(e)
                error_str = error_str.replace('https://m.land.naver.com/', 'WEB:')
                rp(error_str + ' Exception occured; sleep 1 min', msg_type= 'NOTICE')
                time.sleep(60 * 1)

    def process(self, target):
        # if target.created_date != TODAY and not target.is_detail_processed:
        #     # print(self.args.sido, target.article_id, target.created_date)
        #     rp(str(self.args.sido) + ' ' + str(target.created_date) + ' target.created_date != ' + str(TODAY) + '; not processing')
        #     raise ValueError('target.created_date != TODAY')
        #     target.has_detail_text = True
        #     target.is_detail_failed = True
        #     target.detail_processed_at = timezone.now()
        #     target.is_live = False
        #     target.is_live_checked_at = timezone.now()
        #     target.save()
        #     return

        if target.has_history:
            history = target.history_set.last()
            if history.has_detail_text:
                rp(self.args.sido + ' ' + str(target.created_date) + ' ' + target.title + ' use history detail')
                target.detail_processed_at = history.detail_processed_at
                target.has_detail_text = history.has_detail_text
                target.is_detail_processed = history.is_detail_processed
                target.is_detail_failed = history.is_detail_failed
                target.save()
                rp('Wait 1 sec')
                time.sleep(1)
                return

        if target.종류 == '원룸/고시원':
            target.has_detail_text = True
            target.is_detail_failed = True
            target.detail_processed_at = timezone.now()
            target.is_live = False
            target.is_live_checked_at = timezone.now()
            target.save()
            return

        rp(' '.join([
            target.article_id, target.sido, target.sgg, target.emd, target.title
        ]))
        rp(' '.join([
            'target.created_at', str(target.created_at), 'target.updated_at', str(target.updated_at)
        ]))
        result, done_url = curlreq.get(
            f'https://m.land.naver.com/article/info/{target.article_id}?newMobile',
        )
        rp(done_url)
        if '임시적으로 서비스 이용이 제한' in result or result.strip() == '':
            rp('임시적으로 서비스 이용이 제한', msg_type= 'NOTICE')
            raise Exception('임시적으로 서비스 이용이 제한')

        if '찾으시는 페이지는 주소를 잘못' in result:
            print('찾으시는 페이지는 주소를 잘못')
            target.detail_text = result
            target.has_detail_text = True
            target.is_detail_failed = True
            target.detail_processed_at = timezone.now()
            target.is_live = False
            target.is_live_checked_at = timezone.now()
            target.save()
            dt_util.sleep_random()
        else:
            target.detail_text = result
            target.has_detail_text = True
            target.is_detail_failed = False
            target.detail_processed_at = timezone.now()
            target.is_live = True
            target.is_live_checked_at = timezone.now()
            target.save()
            dt_util.sleep_random()
