from django.conf import settings
from common.util.romsg import rp

from common.util.romsg import send as romsg_send
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models import QuerySet

import common.util.datetime_util as dt_util
import common.util.str_util as str_util
from common.util.logger import RoLogger
logger = RoLogger()
from argparse import Namespace
from common.util import curlreq

import rawarticle.models as rawarticle_models

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

ZOOM_LEVEL = 12
class ClusterCollector(object):

    def __init__(self, args={}):
        self.args = args

    def run(self):
        print('run ClusterCollector', self.args)
        # shell_plus
        # Region.objects.all().update(update_end_time='2000-01-01')
        # Cluster.objects.all().delete()
        self.collect()

    def collect(self):
        q = Q()
        print('settings.EMD_TARGETS', settings.EMD_TARGETS)
        for juso in settings.EMD_TARGETS:
            print(juso)
            sido, sgg, _ = juso.split()
            q.add(Q(sido= sido, sgg= sgg), q.OR)

        # 읍면동 타겟이 없을 때 시도 타겟으로 대체
        # 한 달에 한 번? 정도 전체 돌릴 때 사용
        if len(settings.EMD_TARGETS) == 0:
            for target in settings.REGION_TARGETS:
                q.add(Q(sido= target), q.OR)

        targets = rawarticle_models.Region.objects.filter(
            q
        ).filter(
            regionType= 'emd',
            # title= '해안동4가'
        ).exclude(
            # update_end_time= timezone.now().date()
        ).order_by(
            'title',
            # 'update_end_time'
        )

        print('targets', targets.count())

        for target in targets:
            target.update_start_time = timezone.now()
            target.save()
            self.collect_by_region(target)
            target.update_end_time = timezone.now()
            target.save()
            dt_util.sleep_random()

    def collect_by_region(self, target):
        rp('Collect Cluster : ' + target.sido + ' ' + target.sgg + ' ' + target.title)
        result, url = curlreq.get('https://m.land.naver.com/cluster/clusterList', {
            "view": "atcl",
            "cortarNo": target.code,
            "z": ZOOM_LEVEL,
            "rletTpCd": "APT%3AOPST%3AVL%3AABYG%3AOBYG%3AJGC%3AJWJT%3ADDDGG%3ASGJT%3AHOJT%3AJGB%3AOR%3AGSW%3ASG%3ASMS%3AGJCG%3ASG%3AGM%3ATJ%3AAPTHGJ",
            'tradTpCd': 'A1%3AB1%3AB2%3AB3',
        })
        print(url)
        result_obj = json.loads(result)
        # print(result_obj)
        cluster_list = result_obj['data']['ARTICLE']
        if len(cluster_list) == 0:
            cluster = {}
            cluster['sido'] = target.sido
            cluster['sgg'] = target.sgg
            cluster['emd'] = target.title
            cluster['parent'] = target.code
            cluster['count'] = 0
            cluster['z'] = ZOOM_LEVEL
            rawarticle_models.Cluster.objects.update_or_create(
                lgeo= '',
                parent= cluster['parent'],
                defaults= cluster
            )
            return

        for cluster in cluster_list:
            if 'itemId' in cluster:
                # count가 1개인 경우 itemId가 있다 하더라도 lgeo를 저장해양 함
                if cluster['count'] > 1:
                    continue
                else:
                    del cluster['itemId']
                    del cluster['maxMviFee']
                    del cluster['minMviFee']
                    if cluster.get('prc'): del cluster['prc']
                    del cluster['priceTtl']
                    del cluster['rletNm']
                    del cluster['tradNm']
                    del cluster['tradTpCd']

            if 'z' not in cluster:
                cluster['z'] = ZOOM_LEVEL

            cluster['sido'] = target.sido
            cluster['sgg'] = target.sgg
            cluster['emd'] = target.title
            cluster['parent'] = target.code
            print(' '.join([
                cluster['sido'],
                cluster['sgg'],
                cluster['emd'],
                cluster['lgeo'],
                str(cluster['count'])
            ]))
            rawarticle_models.Cluster.objects.update_or_create(
                lgeo= cluster['lgeo'],
                parent= cluster['parent'],
                defaults= cluster
            )

        target.update_end_time = timezone.now()
        target.save()
