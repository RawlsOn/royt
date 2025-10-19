from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date, timedelta
import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from django.core.files import File
from argparse import Namespace
import requests
from common.util import curlreq
import json

# ./manage.py crawl_tester

class Command(BaseCommand):

    def add_arguments(self, parser):
        pass
        # parser.add_argument(
        #     '--file_path',
        #     type=str,
        #     required=True
        # )
        # parser.add_argument(
        #     '--upload_day',
        #     type=str,
        #     default='01'
        # )
        # parser.add_argument(
        #     '--admin_email',
        #     type=str,
        #     default=settings.ADMIN_EMAIL
        # )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        print('run_crawl_tester.py')

        # 지역코드 찾기
        # https://m.land.naver.com/map/37.530126:127.123771:12:1174000000/APT:SG/A1:B1:B2#regionStep1
        # 여기서 서울시를 넣어서 찾으면 구 데이터를 찾을 수 있음
        # https://m.land.naver.com/map/getRegionList?cortarNo=1100000000&mycortarNo=1100000000

        # 구를 가지고 동 데이터를 찾기
        # https://m.land.naver.com/map/getRegionList?cortarNo=1168000000&mycortarNo=1168000000

        # 클러스트 리스트 받기
        # https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo=1168010300&rletTpCd=SG&tradTpCd=A1%3AB1%3AB2&z=14&lat=37.482968&lon=127.0634&btm=37.459705&lft=127.0372646&top=37.5062238&rgt=127.0895354&pCortarNo=14_1168010300&addon=COMPLEX&bAddon=COMPLEX&isOnlyIsale=false
        # https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo=1168010300&rletTpCd=APT&tradTpCd=A1%3AB1%3AB2&z=14&lat=37.482968&lon=127.0634&btm=37.459705&lft=127.0372646&top=37.5062238&rgt=127.0895354&pCortarNo=14_1168010300&addon=COMPLEX&bAddon=COMPLEX&isOnlyIsale=false
        # https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo=1168010300&rletTpCd=APT&tradTpCd=A1%3AB1%3AB2&z=14&lat=37.482968&lon=127.0634
        #
        # https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo=1168010300&rletTpCd=APT&tradTpCd=A1%3AB1%3AB2&z=14&lat=37.482968&lon=127.0634&btm=37.459705&lft=127.0372646&top=37.5062238&rgt=127.0895354&pCortarNo=14_1168010300&addon=SCHOOL

        # https://cocoabba.tistory.com/58

        # _tradTpCd = [{tagCd: 'A1', uiTagNm: '매매'},
        #              {tagCd: 'B1', uiTagNm: '전세'},
        #              {tagCd: 'B2', uiTagNm: '월세'},
        #              {tagCd: 'B3', uiTagNm: '단기임대'}];
        # _rletTpCd = [{tagCd: 'APT', uiTagNm: '아파트'}, {tagCd: 'OPST', uiTagNm: '오피스텔'}, {tagCd: 'VL', uiTagNm: '빌라'},
        #              {tagCd: 'ABYG', uiTagNm: '아파트분양권'}, {tagCd: 'OBYG', uiTagNm: '오피스텔분양권'}, {tagCd: 'JGC', uiTagNm: '재건축'},
        #              {tagCd: 'JWJT', uiTagNm: '전원주택'}, {tagCd: 'DDDGG', uiTagNm: '단독/다가구'}, {tagCd: 'SGJT', uiTagNm: '상가주택'},
        #              {tagCd: 'HOJT', uiTagNm: '한옥주택'}, {tagCd: 'JGB', uiTagNm: '재개발'}, {tagCd: 'OR', uiTagNm: '원룸'},
        #              {tagCd: 'GSW', uiTagNm: '고시원'}, {tagCd: 'SG', uiTagNm: '상가'}, {tagCd: 'SMS', uiTagNm: '사무실'},
        #              {tagCd: 'GJCG', uiTagNm: '공장/창고'}, {tagCd: 'GM', uiTagNm: '건물'}, {tagCd: 'TJ', uiTagNm: '토지'},
        #              {tagCd: 'APTHGJ', uiTagNm: '지식산업센터'}];

        # curlreq.get('https://m.land.naver.com/cluster/clusterList', {
        #     "view": "atcl",
        #     "cortarNo": "1168010300",
        #     "z": 14,
        #     "lon": "127.0634",
        #     "lat": "37.482968",
        # })

        # https://m.land.naver.com/cluster/ajax/articleList?itemId=212033230213&mapKey=&lgeo=212033230213&rletTpCd=APT%3AOPST%3AVL%3AABYG%3AOBYG%3AJGC%3AJWJT%3ADDDGG%3ASGJT%3AHOJT%3AJGB%3AOR%3AGSW%3ASG%3ASMS%3AGJCG%3AGM%3ATJ%3AAPTHGJ&tradTpCd=A1%3AB1%3AB2%3AB3&z=16&cortarNo=1168010300&showR0=

        #  { 'count': 1274,
        # 'lat': 37.48125,
        # 'lgeo': '2120332213',
        # 'lon': 127.05332031,
        # 'psr': 0.8},

        # https://m.land.naver.com/cluster/ajax/articleList?itemId=212033230231&lgeo=212033230231&mapKey=&cortarNo=1168010300&showR0=&rletTpCd=APT&tradTpCd=A1&z=16

        # https://m.land.naver.com/cluster/articleList?itemId=2120332213&lgeo=2120332213&mapKey=&cortarNo=1168010300&showR0=&rletTpCd=APT&z=14&sort=dates

        # https://m.land.naver.com/cluster/ajax/articleList?itemId=2120332213&lgeo=2120332213&mapKey=&cortarNo=1168010300&showR0=&rletTpCd=APT&z=14&sort=dates


        # https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo=1168010300&rletTpCd=APT%3AOPST%3AVL%3AABYG%3AOBYG%3AJGC%3AJWJT%3ADDDGG%3ASGJT%3AHOJT%3AJGB%3AOR%3AGSW%3ASG%3ASMS%3AGJCG%3AGM%3ATJ%3AAPTHGJ&tradTpCd=A1%3AB1%3AB2%3AB3&z=16&lat=37.482968&lon=127.0634&btm=37.4767357&lft=127.0568661&top=37.4891998&rgt=127.0699339&pCortarNo=&addon=COMPLEX&isOnlyIsale=false

        # https://m.land.naver.com/cluster/ajax/articleList?itemId=212033230231&mapKey=&lgeo=212033230231&rletTpCd=SG%3AGM%3ATJ&tradTpCd=A1%3AB1%3AB2%3AB3&z=16&lat=37.482968&lon=127.0634

        # https://m.land.naver.com/cluster/ajax/articleList?itemId=212033230231&lgeo=212033230231&mapKey=&cortarNo=1168010300&showR0=&rletTpCd=SG%3AGM%3ATJ&tradTpCd=A1%3AB1%3AB2%3AB3&z=16

        # https://m.land.naver.com/cluster/ajax/articleList?itemId=212033230231&lgeo=212033230231&mapKey=&cortarNo=1168010300&showR0=&rletTpCd=APT%3AOPST%3AVL%3AABYG%3AOBYG%3AJGC%3AJWJT%3ADDDGG%3ASGJT%3AHOJT%3AJGB%3AOR%3AGSW%3ASG%3ASMS%3AGJCG%3ASG%3AGM%3ATJ%3AAPTHGJ&tradTpCd=A1%3AB1%3AB2%3AB3&z=16&sort=dates&page=1

        # curlreq.get('https://m.land.naver.com/cluster/ajax/articleList', {
        #     'itemId': '212033230231',
        #     'mapKey': '',
        #     'lgeo': '212033230231',
        #     'cortarNo': "1168010300",
        #     'showR0': ''
        # })

        # result_obj = curlreq.get('https://m.land.naver.com/article/info/2330266035?newMobile')

        # print(result_obj)

        # curlreq.save_article('2330794282')

        # result = subprocess.check_output([
        #     "curl",
        #     clusterListUrl
        # ], encoding='utf-8')
        # pp.pprint(json.loads(result))

        # articleListUrl = 'https://m.land.naver.com/cluster/ajax/articleList?itemId=21221102&mapKey=&lgeo=21221102&rletTpCd=APT&tradTpCd=A1%3AB1%3AB2&z=12&lat=37.517408&lon=127.047313&btm=37.4243553&lft=126.9427712&top=37.6103448&rgt=127.1518548&cortarNo=1168000000&showR0='
        # result = subprocess.check_output([
        #     "curl",
        #     articleListUrl
        # ], encoding='utf-8')
        # pp.pprint(json.loads(result))


        # url = "https://m.land.naver.com/search/result/서울특별시 강남구"
        url = "https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo=4119011500&rletTpCd=SG&tradTpCd=A1&z=14&lat=37.46801&lon=126.82423&btm=37.4349629&lft=126.7418325&top=37.5010425&rgt=126.9066275&pCortarNo=&addon=COMPLEX&isOnlyIsale=false"
        res = requests.get(url)
        # res.raise_for_status()

        print(res.text)

        # soup = (str)(BeautifulSoup(res.text, "lxml"))

        # print(soup)