from django.conf import settings

from common.util.romsg import rp
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
from django.db import connection

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models import QuerySet
import common.util.datetime_util as dt_util
from common.util import curlreq

import common.util.datetime_util as datetime_util
import common.util.str_util as str_util
import common.util.juso_util as juso_util
from common.util.logger import RoLogger
logger = RoLogger()
from argparse import Namespace
from bs4 import BeautifulSoup
from django.apps import apps
import core.models as core_models
# from main.workers.ArticleHtmlGetter import ArticleHtmlGetter

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# ./manage.py run_article_pnu_writer --sido=경기도

LIMIT = 10000
class ArticlePnuWriter(object):

    def __init__(self, args={}):
        self.args = args

    def run(self):
        print('run ArticlePnuWriter', self.args)
        sido = self.args.sido
        model = apps.get_model('core', 'Article' + sido)
        self.model = model
        print('counting...')
        targets = model.objects.filter(
            pnu_processed_at__isnull= True,
            pnu__isnull= False,
        )
        self.total_count = targets.count()
        print('total_count', self.total_count)
        if self.total_count == 0:
            rp('nothing to do')
            return

        self.idx = 0
        while True:
            self.process()

    def process(self):
        rp('raw querying...')
        QUERY = f"""
SELECT * FROM core_article{self.args.sido}
WHERE pnu IS NOT NULL and pnu_processed_at IS NULL
ORDER BY pnu
LIMIT {LIMIT}
"""
        print(QUERY)
        targets = self.model.objects.raw(QUERY)
        if len(targets) == 0:
            rp('nothing to do')
            print('total_count', self.total_count)
            raise Exception('nothing to do')

        for target in targets:
            self.idx += 1
            str_util.print_progress(
                self.idx,
                self.total_count,
                gap= 10,
                info= self.args.sido + ' article pnu writing...'
            )
            self.process_target(target)
            # break

    def process_target(self, target):
        # print('target', target, target.pnu)
        folder = os.path.join(
            '/usr', 'data', 'onenaverlandcrawler-local', 'PNU',
            target.sido, target.sgg, target.emd
        )
        # make folder
        if not os.path.exists(folder):
            os.makedirs(folder)
        # set file name as pnu
        file_name = os.path.join(folder, target.pnu)
        # write target to file
        # print(file_name)
        # check file exists
        if os.path.exists(file_name):
            # 되게 많네
            # print('Appendable : PNU exists: ' + file_name)
            # raise Exception('PNU exists: ' + file_name)
            pass

        with open(file_name, 'a') as f:
            to_write = target.to_obj
            to_write.pop('detail_text')
            # pp.pprint(to_write)
            # make json
            to_write = json.dumps(to_write, ensure_ascii=False)
            f.write(to_write + '\n')

        target.pnu_processed_at = timezone.now()
        target.save()
