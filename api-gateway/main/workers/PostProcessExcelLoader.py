from django.conf import settings

import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

from common.util import juso_util, model_util, str_util
from django.contrib.gis.geos import Point

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone

import openpyxl

import geoinfo.models as geoinfo_models
import main.models as main_models
import core.models as core_models
import user.models as user_models

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

class PostProcessExcelLoader(object):

    def __init__(self, args={}):
        self.args = args

    def run(self):
        print('run PostProcessExcelLoader', self.args)
        self.raw_data = {}

        targets = geoinfo_models.GeoUnit.objects.filter(pnu__isnull=False)
        # print(targets.count())
        # print(targets.first().to_obj)

        targets = targets.values(
            'pnu'
        ).annotate(
            Count('id')
        ).order_by().filter(
            id__count__gt=1
        )

        print('dupe', targets.count())
        print(targets.first())

        dupe_pnus = [x['pnu'] for x in targets]

        # 이게 끝나고 여러 개의 PNU가 남아있는데 이렇게 되는 이유는
        # 엑셀에서 데이터를 넣을 때 같은 지번이라도 주소_input값이 다를 수 있기 때문이다.
        # 시를 안 쓴다든가, 끝에 호수가 추가된다든가
        # 만약 주소_input을 안 쓰고 제대로 된 주소만 DB에 가지고 있는다고 하면
        # 엑셀을 로드할 때마다 불완전한 주소_input은 주소API를 호출하게 된다.
        # 뭐가 더 나은 설계일까,,
        # 이대로 dup을 용인하고, 차후에 수정하는 것이 나을 것인지
        # 처음부터 dup이 안 생기도록 하지만
        # 엑셀로드할 떄마다 주소 API 호출량이 많아지는 것을 할 것인지
        # 일단은 프로젝트가 끝났으니까 이대로 두도록 한다.
        # 차기 프로젝트를 수주할 경우 그 때 고맨하도록 한다.

        for pnu in dupe_pnus:
            units = geoinfo_models.GeoUnit.objects.filter(pnu= pnu)
            master_unit = units.first()
            slave_units = [x for x in units.all()][1:]
            # print('------------------------------')
            # print('master', master_unit.id, master_unit.주소_input)
            for unit in slave_units:
                # print('slave:', unit.id, unit.주소_input)
                토지s = core_models.토지.objects.filter(geo_unit_id= unit.id)
                건물s = core_models.건물.objects.filter(geo_unit_id= unit.id)
                상가s = core_models.상가.objects.filter(geo_unit_id= unit.id)

                for 토지 in 토지s:
                    토지.geo_unit_id= master_unit.id
                    토지.save()

                for 건물 in 건물s:
                    건물.geo_unit_id= master_unit.id
                    건물.save()

                for 상가 in 상가s:
                    상가.geo_unit_id= master_unit.id
                    상가.save()

