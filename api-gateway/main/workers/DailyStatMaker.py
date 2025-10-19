from django.conf import settings

from common.util.romsg import rp
import subprocess
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone as django_timezone
from pytz import timezone
from django.db.models import QuerySet

import common.util.datetime_util as dt_util
import common.util.str_util as str_util
from common.util.logger import RoLogger
logger = RoLogger()
from argparse import Namespace
from common.util.AwsUtil import AwsUtil
from django.apps import apps

import main.models as main_models
# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# ./manage.py run_daily_stat_maker

class DailyStatMaker(object):

    def __init__(self, args={}):
        self.args = args

    def run(self):
        print('run Daily Stat Maker')
        if self.args.interval == 'daily':
            self.run_daily()
        elif self.args.interval == 'weekly':
            self.run_weekly()
        elif self.args.interval == 'today':
            self.run_today()
        self.yesterday = django_timezone.now().date() - timedelta(days=1)
        targets = main_models.TimeTrack.objects.filter(
            created_date= self.yesterday
        ).all()

    def run_weekly(self):
        monday = dt_util.get_monday()
        # 수면시간 때문에 필요한데 일단 보류
        one_day_before = monday - timedelta(days=1)

        targets = main_models.TimeTrack.objects.filter(
            track_time__gte= monday,
            track_time__lte= dt_util.now().date()
        ).all().order_by('track_time')

        self.make_stat(targets)

    def run_today(self):
        today = dt_util.now().date()
        yesterday_evening = (dt_util.now() - timedelta(days=1)).replace(hour=20)

        self.yesterday_sleep_filter = Q(track_time__gte= yesterday_evening, top_category__name='수면')

        Q(sido='경기도')|Q(sido='서울시')|Q(sido='인천시')
        targets = main_models.TimeTrack.objects.filter(
            Q(track_time__gte= today)|
            self.yesterday_sleep_filter
        ).all().order_by('track_time')

        self.make_stat(targets)

        # pp.pprint(simple_bottom_sum_map)
        yesterday_sleep = main_models.TimeTrack.objects.filter(self.yesterday_sleep_filter).first()
        yesterday_sleep_elapsed = yesterday_sleep.track_time.replace(hour=0).replace(minute=0).replace(second=0) + timedelta(days=1) - yesterday_sleep.track_time
        # print(yesterday_sleep_elapsed)
        total_recorded_time_wo_yesterday_sleep = self.total_recorded_time - yesterday_sleep_elapsed.total_seconds()
        total_recorded_time_wo_yesterday_sleep = dt_util.sec_to_str(total_recorded_time_wo_yesterday_sleep)
        self.total_recorded_time = dt_util.sec_to_str(self.total_recorded_time)
        # pp.pprint(bottom_sum_map['직장동료'])

        print('\n')
        indent = 20
        print(f'{str_util.fmt("총기록시간", indent, "l")} {str_util.fmt(self.total_recorded_time, indent, "r")}')
        print(f'{str_util.fmt("오늘기록시간", indent, "l")} {str_util.fmt(total_recorded_time_wo_yesterday_sleep, indent, "r")}')

        print('\n')

    def make_stat(self, targets):
        target_dict_list = []
        bottom_sum_map = {}
        self.total_recorded_time = 0.0
        mid_sum_map = {}
        top_sum_map = {}
        for target in targets:
            target_dict_list.append(target.to_obj)

        for idx, target in enumerate(target_dict_list):
            aug_target = target
            next_target = target_dict_list[idx+1] if idx+1 < len(target_dict_list) else None
            if next_target:
                aug_target['start_at'] = target['track_time']
                aug_target['end_at'] = next_target['track_time']
                aug_target['elapsed'] = aug_target['end_at'] - aug_target['start_at']
            else:
                aug_target['start_at'] = target['track_time']
                # aug_target['end_at'] = target['track_time'].replace(hour=0).replace(minute=0).replace(second=0) + timedelta(days=1)
                aug_target['end_at'] = dt_util.now()
                aug_target['elapsed'] = aug_target['end_at'] - aug_target['start_at']

            # 정리;; 지저분;; 나중에 필요없게 되겠지만,,
            if target['top_category'] == '수면':
                target['mid_category'] = 'N/A'

            if target['mid_category'] == 'N/A':
                target['mid_category'] = target['top_category']

            if target['bottom_category'] == 'N/A':
                target['bottom_category'] = target['mid_category']


            target['full'] = '\t'.join([
                target['track_time'].strftime('%Y-%m-%d'),
                target['top_category'],
                target['mid_category'],
                target['bottom_category'][:3],
                target['start_at'].strftime('%H:%M:%S'),
                target['end_at'].strftime('%H:%M:%S'),
                str(target['elapsed'])
            ])

            target_dict_list[idx] = aug_target

        for idx, target in enumerate(target_dict_list):
            self.total_recorded_time += target['elapsed'].total_seconds()
            if target['bottom_category'] not in bottom_sum_map:
                bottom_sum_map[target['bottom_category']] = {
                    'elapsed': target['elapsed'].total_seconds(),
                    'history': [target]
                }
            else:
                # print("target['elapsed']", target['elapsed'])
                target_category = bottom_sum_map[target['bottom_category']]
                target_category['elapsed'] += target['elapsed'].total_seconds()
                target_category['history'].append(target)

        # for key, val in bottom_sum_map.items():
        #     bottom_sum_map[key]['elapsed'] = dt_util.sec_to_str(val['elapsed'])

        # pp.pprint(bottom_sum_map)

        simple_bottom_sum_map = {}
        for key, val in bottom_sum_map.items():
            simple_bottom_sum_map[key] = val['elapsed']

        ordered_list = []
        for key, val in simple_bottom_sum_map.items():
            ordered_list.append([key, val])

        ordered_list = sorted(ordered_list, key=lambda x: x[1], reverse=True)

        pp.pprint(ordered_list)

        print('\n')
        for key, val in ordered_list:
            # print(f'{key: <25} {val}')
            # print('%s %s %s | %s |'%(str_util.fmt(key, 10, 'l'), str_util.fmt(val, 10, 'l')))
            indent = 20
            val = dt_util.sec_to_str(val)
            print(f'{str_util.fmt(key, indent, "l")} {str_util.fmt(val, indent, "r")}')