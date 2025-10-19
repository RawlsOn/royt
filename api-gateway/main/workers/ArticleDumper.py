from django.conf import settings

from common.util.romsg import rp
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
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
import core.models as core_models
# from main.workers.ArticleHtmlGetter import ArticleHtmlGetter

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# ./manage.py run_article_dumper --sido=서울시 --종류=건물

LIMIT = 1000
class ArticleDumper(object):

    def __init__(self, args={}):
        self.args = args

    def run(self):
        self.first = True
        self.offset = 0
        self.done_count = 0
        print('counting...', self.args.sido, self.args.종류)
        # self.total_count = core_models.Article서울시.objects.filter(
        #     # 종류__in= ['토지', '건물', '상가'],
        #     종류= self.args.종류,
        #     is_detail_processed= True,
        #     is_detail_failed= False,
        # ).count()
        self.total_count = 1000
        while True:
            go_on = self._run()
            self.offset += 1
            if not go_on:
                rp('Nothing to do. Stop.')
                return

    def _run(self):
        print('total_count', self.total_count)
        print('querying...')
        QUERY = f"""
SELECT * FROM core_article{self.args.sido}
WHERE 종류='{self.args.종류}'
    and is_detail_processed= 1
    and is_detail_failed= 0
    LIMIT {LIMIT} OFFSET {self.offset * LIMIT}
"""
        model = apps.get_model('core', 'Article' + self.args.sido)
        targets = model.objects.raw(QUERY)
        print('len(targets)', len(targets))
        time.sleep(1)
        if len(targets) == 0:
            return False
        self._write(targets)
        return True

    def _write(self, targets):
        # write to csv
        BASE_DIR = '/usr/data/onenaverlandcrawler-local/dump/20230817'
        with open(
            BASE_DIR + '/' + self.args.sido + '_' + self.args.종류 + '.csv',
            'w',
            newline='',
            encoding='utf-8'
        ) as f:
            print('open file..')
            writer = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            to_write_list = []
            print('requerying...')
            for target in targets:
                self.done_count += 1
                str_util.print_progress(self.done_count, self.total_count, info='write csv', gap=100)
                to_write = target.__dict__
                to_delete = [
                    '_state','created_at','updated_at',
                    'gijun_date','gijun_date_str',
                    'has_detail_text','detail_text','is_detail_processed',
                    'is_detail_failed','detail_processed_at','has_sel_text',
                    'sel_text','is_sel_processed','sel_processed_at',
                    'dev_memo','dev_memo2','dev_memo3',
                    '기보증금','기월세','난방1','난방2','방수',
                    '욕실수','현관구조','건설사','상세설명'
                ]
                for to_del in to_delete:
                    del to_write[to_del]

                if self.first:
                    writer.writerow(to_write.keys())
                    self.first = False
                    continue

                # csv를 컨트롤캐릭터로 합치고 있을지 모르는 탭 제거하고,
                # 뉴라인제거하고
                # 다시 풀어서 넣어야 할 듯
                # excel에서 보이게 try :
                # https://stackoverflow.com/questions/38015124/issue-with-utf-encoding-on-csv-file-for-excel
                newline_removed = [
                    x.replace('\n', '').replace('\r', '') for x in list(to_write.values())
                ]
                writer.writerow([self.done_count] + newline_removed)

고