from django.conf import settings

import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models import QuerySet

import common.util.datetime_util as datetime_util
import common.util.str_util as str_util
from common.util.logger import RoLogger
logger = RoLogger()

import tenniscode.models as tenniscode_models

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from .RankFileLoader import RankFileLoader


class OpenRankFileLoader(RankFileLoader):
    def process_player(self, row):
        ranking, name, club1, club2, _, _, _, _ = row
        player, _ = tenniscode_models.Player.objects.get_or_create(
            name= name,
            main_club_str= club1,
            defaults= {
                '기준일': self.기준일,
            }
        )
        self.player = player

        self.process_club(club1, player)
        self.process_club(club2, player)

    def process_performance(self, row):
        _, _, club1, club2, competition_title, result, point, match_date = row

        if result == '4위': result = '4강'
        if result == '3위': result = '4강'

        # 포인트가 없는 경우는 부정선수라서 0점 처리된 것인가?
        # 2022 신인부 3273라인 박용학 별내 카타회장배 1위 점수가 0. 2019/10/19
        if point == '0': return

        category_1, category_2 = self._make_competition_category(competition_title, result, point)
        comp, _ = tenniscode_models.Competition.objects.get_or_create(
            title= competition_title,
            category= category_2,
            defaults= {
                'comp_type': '랭킹대회',
                'date': match_date.replace('/', '-').replace('.', '-')
            }
        )

        # lt_point = self._make_lt_point(result, comp.category)

        # 0이면 1점 줌
        # if lt_point == 0: lt_point = 1

        performance_level = ''
        if category_1 == 'open': performance_level = '상급자부(남자)'
        elif category_1 == 'challenger': performance_level = '신인부(남자)'

        # 단체전은 제외함
        if performance_level != '':
            tenniscode_models.Performance.objects.get_or_create(
                competition= comp,
                player= self.player,
                defaults= {
                    'point_type': 'KATA',
                    'performance_level': performance_level,
                    'result': result,
                    'point': point,
                    'match_date': datetime.strptime(match_date.replace('/', '-').replace('.', '-'), "%Y-%m-%d"),
                }
            )

