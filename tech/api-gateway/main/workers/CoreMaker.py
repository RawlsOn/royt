# 2024-05-07
# 표준 코어메이커
# cp /Users/kimmyounghoon/Works/mkay/common/api-gateway/main/workers/* ./api-gateway/main/workers/

from django.conf import settings
from common.util.romsg import rp

from common.util import juso_util, model_util, str_util
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv, random
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

from common.util import datetime_util, dict_util
from django.contrib.gis.geos import Point
from django.apps import apps

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone

pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from common.util.RoPrinter import RoPrinter
PRINT_GAP = 10

class CoreMaker(object):

    def __init__(self, args={}):
        printer = RoPrinter(f'{args.baseapp} CoreMaker')
        self.rp = printer.rp
        self.ps = str_util.ProgressShower(gap=PRINT_GAP, info=f'{args.ro_gijun_date} {args.baseapp} CoreMaker')
        self.ps.printer = printer
        self.args = args

    def run(self):
        print(f'run {self.args.baseapp} CoreMaker')
        self.Proto = apps.get_model(f'{self.args.baseapp}proto', 'Proto')
        self.Core = apps.get_model(f'{self.args.baseapp}core', 'Core')
        self.RoGijunDate = apps.get_model(f'{self.args.baseapp}core', 'RoGijunDate')
        self.GijunDate = apps.get_model(f'{self.args.baseapp}core', 'GijunDate')
        self.make_core()

    def make_core(self):
        print('make_core')

        self.rp(f'proto count: {self.Proto.objects.count()}')
        self.rp(f'core count: {self.Core.objects.count()}')

        self.rp('querying...')
        proto_ids = self.Proto.objects.all().values_list('id', flat=True)

        # proto_ids = proto_ids[:10]

        self.ps.total = len(proto_ids)
        for proto_id in proto_ids:
            self.ps.show()
            proto = self.Proto.objects.get(id=proto_id)
            # pp.pprint(proto.__dict__)
            new_entry = proto.data_to_core(self.args.ro_gijun_date)
            if new_entry is None:
                proto.delete()
                continue

            # pp.pprint(new_entry)
            # print('center', new_entry['center'])
            core = self.Core.objects.filter(
                code= new_entry['code'],
            ).first()

            if not core:
                # print('-----------core 없음')
                self._create_core(new_entry)
                proto.delete()
                continue
            else:
                # print('-----------core 있음')
                core_dict = core.__dict__
                is_diff, reason = dict_util.is_diff(core_dict, new_entry)
                if is_diff:
                    # print('다르면')
                    core = self._create_core(new_entry, core)
                    # 이거 잘 되는지 체크해야 함
                    reason.append(new_entry.gijun_date)
                    core.reason_json = dict_util.merge_json(
                        core.reason_json,
                        json.dumps({'diff': reason}, ensure_ascii=False)
                    )
                    core.save()
                else:
                    # print('같으면')
                    self._add_dates(core, new_entry)

            proto.delete()

    def _create_core(self, new_entry, core=None):
        # print('_create_core')
        # pp.pprint(new_entry)

        copied_new_entry = new_entry.copy()

        ro_gijun_date = new_entry['ro_gijun_date']
        del new_entry['ro_gijun_date']

        if 'gijun_date' in new_entry:
            gijun_date = new_entry['gijun_date']
            del new_entry['gijun_date']

        # pp.pprint(new_entry)
        # 한 ro_gijun_date에 두 개 이상의 code가 있을 수 있음
        # 정부데이터 오류같긴 한데
        # 그러면 update하고 reason에 추가함
        if core:
            # print('-------has core')
            core, created = self.Core.objects.update_or_create(
                code= core.code,
                defaults= new_entry
            )
        else:
            new_entry['init_ro_gijun_date_str'] = ro_gijun_date
            core = self.Core.objects.create(**new_entry)
        self._add_dates(core, copied_new_entry)

        return core

    def _add_dates(self, core, new_entry):
        # print('_add_dates------------')
        ro_gijun_date = new_entry['ro_gijun_date']
        got, created = self.RoGijunDate.objects.get_or_create(
            id= ro_gijun_date,
            defaults=dict(
                d= ro_gijun_date,
                month= ro_gijun_date[:7],
                year= ro_gijun_date[:4],
            )
        )
        core.ro_gijun_dates.add(got)

        if 'gijun_date' in new_entry:
            gijun_date = new_entry['gijun_date']
            got, created = self.GijunDate.objects.get_or_create(
                id= gijun_date,
                defaults=dict(
                    d= gijun_date,
                    month= gijun_date[:7],
                    year= gijun_date[:4],
                )
            )
            core.gijun_dates.add(got)
