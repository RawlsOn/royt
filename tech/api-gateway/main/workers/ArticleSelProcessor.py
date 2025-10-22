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

import common.util.datetime_util as datetime_util
import common.util.str_util as str_util
from common.util.logger import RoLogger
logger = RoLogger()
from argparse import Namespace
from bs4 import BeautifulSoup
from django.apps import apps
import rawarticle.models as rawarticle_models
from main.workers.ArticleHtmlGetter import ArticleHtmlGetter

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# echo 'CORE_DATABASE={"ENGINE": "django.db.backends.sqlite3","NAME":"/Users/kimmyounghoon/Library/Mobile Documents/com~apple~CloudDocs/cloud/data/onenaverlandcrawler-local/core.sqlite3","OPTIONS": {"timeout": 5}}' >> .env
# ./manage.py run_article_sel_processor
class ArticleSelProcessor(object):

    def __init__(self, args={}):
        self.args = args

    def run(self):
        print('run ArticleSelGetter', self.args)
        # parser = Parser(self.args)
        self.html_getter = ArticleHtmlGetter()
        # self.parser = Parser(self.args)
        # self.post_parser = PostParser(self.args)
        while True:
            targets = rawarticle_models.ProtoArticle.objects.all()
            total_count = targets.count()
            targets.filter(
                has_ssl_text= False
            )
            target_count = targets.count()
            str_util.print_progress(target_count, total_count, gap= 1, info='getting article sel...')
            if target_count == 0:
                rp('No target to collect sel detail')
                return


            self.process(targets[:100])

    def process(self, targets):

        for target in targets:
            html = self.html_getter.run(target.article_id)
            target.ssl_text = html
            target.has_sel_text = True
            target.save()
            dt_util.sleep_random()
            # # html = ''

            # # FOLDER = '/usr/data/onenaverlandcrawler-local/article_html'
            # # target_file_name = FOLDER + '/ar_2330105223'
            # # with open(target_file_name, 'r') as f:
            # #     html = f.read()

            # parser_result = self.parser.run(html)
            # post_parser_result = self.post_parser.run(html)
            # result = {**parser_result, **post_parser_result}
            # self._save(target, result)
            break

    def _save(self, target, result):
        final = {**target.__dict__, **result}
        got = self.__get_core_article_model(target.sido)(final)
        got.is_detail_updated = True
        got.save()

    def __get_core_article_model(self, sido):
        return apps.get_model('core', 'Article' + sido)

class PostParser(object):
    def __init__(self, args={}):
        self.args = args

    def run(self, html):

        doc = {}
        near = {}
        route = []

        soup = BeautifulSoup(html, 'html.parser')
        f_list = soup.find("div", class_="detail_facilities_list")
        near['버스정류장'] = self._find_near(f_list, 'type_bus')
        near['지하철역'] = self._find_near(f_list, 'type_subway')
        near['어린이집'] = self._find_near(f_list, 'type_infant')
        near['유치원'] = self._find_near(f_list, 'type_child')
        near['학교'] = self._find_near(f_list, 'type_school')
        near['병원'] = self._find_near(f_list, 'type_hospital')
        near['주차장'] = self._find_near(f_list, 'type_parking')
        near['마트'] = self._find_near(f_list, 'type_market')
        near['편의점'] = self._find_near(f_list, 'type_convenience')
        near['세탁소'] = self._find_near(f_list, 'type_washing')
        near['은행'] = self._find_near(f_list, 'type_bank')

        route_list = soup.find(
            'div', class_='detail_time_transport'
        ).find_all(
            'div', class_='detail_item_data'
        )
        for route_html in route_list:
            result = {}
            dest = route_html.find('strong', class_='detail_data_title').text
            elapse = route_html.find('em', class_='detail_text_emphasis').text
            result['호선'], result['역'] = dest.split()
            splitted = elapse.replace('약 ', '').split('분 ')
            result['소요시간(분)'] = int(splitted[0])
            result['수단'] = splitted[1].replace('(', '').replace(')', '')
            route.append(result)

        doc['near'] = near
        doc['route'] = route
        return doc

    def _find_near(self, f_list, class_):
        found = f_list.find('div', class_=class_)
        if not found:
            return None
        return int(found.find(
            'dd', class_='detail_info_data'
        ).text.replace('m', ''))

class Parser(object):
    def __init__(self, args={}):
        self.args = args

