from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date, timedelta
import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from common.util import curlreq

from argparse import Namespace
from main.workers.ArticleCollector import ArticleCollector

# ./manage.py run_article_collector

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
        # 가평읍 = '4182025000' # 경기도 가평군 강평읍
        # print('가평읍')
        # self.emd_run(가평읍)

        # 가정동 = '2826010800' # 인천시 서구 가정동
        # print('가정동')
        # self.emd_run(가정동)

        개포동 = '1168010300' # 서울시 강남구 개포동
        print('개포동')
        self.emd_run(개포동)

        # 강일동 = '1174011000' # 서울시 강남구 강일동
        # print('강일동')
        # self.emd_run(강일동)

    def emd_run(self, emd):
        self.run(emd, z=12)
        self.run(emd, z=13)
        self.run(emd, z=14)

    # https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo=4182025000&rletTpCd=APT%3ATJ&tradTpCd=A1%3AB1%3AB2&z=12
    def run(sefl, emd, z):
        # url = ''.join([
        #     'https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo=',
        #     emd,
        #     '&rletTpCd=APT%3ATJ&tradTpCd=A1%3AB1%3AB2&z=',
        #     str(z)
        # ])
        z13, _ = curlreq.get('https://m.land.naver.com/cluster/clusterList', {
            "view": "atcl",
            "cortarNo": emd,
            "z": z,
            "rletTpCd": "APT%3AOPST%3AVL%3AABYG%3AOBYG%3AJGC%3AJWJT%3ADDDGG%3ASGJT%3AHOJT%3AJGB%3AOR%3AGSW%3ASG%3ASMS%3AGJCG%3ASG%3AGM%3ATJ%3AAPTHGJ",
            'tradTpCd': 'A1%3AB1%3AB2%3AB3',
        })
        z13 = json.loads(z13)
        # pp.pprint(z13)
        z13_clusters = []
        z13_clusters_count = 0
        ordered = sorted(z13['data']['ARTICLE'], key=lambda x: x['lgeo'], reverse=True)
        for x in ordered:
            if not x.get('itemId', None):
                print(x['lgeo'], x['count'])
                z13_clusters.append(x)
                z13_clusters_count += x['count']

        # pp.pprint(z13_clusters)
        print(z, z13_clusters_count)