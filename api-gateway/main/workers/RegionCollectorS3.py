from django.conf import settings

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
from common.util import aws_util
import rawarticle.models as rawarticle_models
import main.models as main_models

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

class RegionCollectorS3(object):

    def __init__(self, args={}):
        self.args = args

    def run(self):
        print('run RegionCollector', self.args)
        self._run_sido()
        # self._run_sgg()
        # self._run_emd()

    def __upload_meta(self, datum, folder):
        local_folder = '/usr/data/onenaverlandcrawler-local/tmp'
        file_name = 'meta.json'
        with open(local_folder + '/' + file_name, 'w') as f:
            f.write(json.dumps(datum, ensure_ascii=False, indent=2))
        aws_util.upload_file(
            local_folder,
            file_name,
            'ro-nogit-data/landn/' + folder + '/' + file_name
        )

    def _run_sido(self):
        sido_obj = json.loads(curlreq.get('https://m.land.naver.com/map/getRegionList?cortarNo=0000000000&mycortarNo='))
        sido_list = sido_obj['result']['list']
        for sido_datum in sido_list:
            result = {
                'title': sido_datum['CortarNm'],
                'code': sido_datum['CortarNo'],
                'cortarType': sido_datum['CortarType'],
                'x': sido_datum['MapXCrdn'],
                'y': sido_datum['MapYCrdn'],
                'regionType': 'sido',
            }
            self.__upload_meta(result)
            break

    def _run_sgg(self):
        targets = rawarticle_models.Region.objects.filter(regionType= 'sido')
        for target in targets:
            print(target)
            sgg_obj = json.loads(
                curlreq.get(
                    'https://m.land.naver.com/map/getRegionList?cortarNo=' + target.code + '&mycortarNo=' + target.code
                )
            )
            sgg_list = sgg_obj['result']['list']
            for sgg_datum in sgg_list:
                result = {
                    'title': sgg_datum['CortarNm'],
                    'code': sgg_datum['CortarNo'],
                    'cortarType': sgg_datum['CortarType'],
                    'x': sgg_datum['MapXCrdn'],
                    'y': sgg_datum['MapYCrdn'],
                    'regionType': 'sgg',
                    'sido': target.title
                }
                rawarticle_models.Region.objects.create(**result)
            dt_util.sleep_random()

    def _run_emd(self):
        rawarticle_models.Region.objects.filter(regionType= 'emd').delete()
        targets = rawarticle_models.Region.objects.filter(
            regionType= 'sgg'
        ).filter(Q(sido='서울시') | Q(sido='경기도') | Q(sido='인천시'))
        for target in targets:
            print(target)
            emd_obj = json.loads(
                curlreq.get(
                    'https://m.land.naver.com/map/getRegionList?cortarNo=' + target.code + '&mycortarNo=' + target.code
                )
            )
            emd_list = emd_obj['result']['list']
            for emd_datum in emd_list:
                result = {
                    'title': emd_datum['CortarNm'],
                    'code': emd_datum['CortarNo'],
                    'cortarType': emd_datum['CortarType'],
                    'x': emd_datum['MapXCrdn'],
                    'y': emd_datum['MapYCrdn'],
                    'regionType': 'emd',
                    'sido': target.sido,
                    'sgg': target.title
                }
                rawarticle_models.Region.objects.create(**result)
            dt_util.sleep_random()
