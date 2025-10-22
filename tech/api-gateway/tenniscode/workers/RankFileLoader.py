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

import tenniscode.models as tenniscode

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

class RankFileLoader(object):

    def __init__(self, args={}):
        self.신인부_페널티 = 10 # 점수를 10으로 나눔
        self.args = args
        self.기준일 = self.args.gijun_date

    def run(self):
        print('run RankFileLoader', self.args)

        with open(self.args.file, 'r') as f:
            csvreader = csv.reader(f)
            idx = 0
            for row in csvreader:
                self.process(idx, row)
                idx += 1

    def process(self, idx, row):
        str_util.print_progress(idx, self.args.lines, self.__class__.__name__)
        if idx < 3: return
        if row[0] != '':
            self.process_player(row)
        else:
            self.process_performance(row)

    def process_club(self, club, player):
        if club != '':
            club_obj, _ = tenniscode.Club.objects.get_or_create(
                    title= club,
                    defaults= {
                        '기준일': self.기준일,
                    }
            )
            player.clubs.add(club_obj)

    def _make_competition_category(self, competition_title, result, point):
        category = self._make_competition_category_inner(competition_title, result, point)
        if category == 'open': return category, '카타 전국대회 상급자부(남자)'
        if category == 'challenger': return category, '카타 전국대회 신인부(남자)'
        if category == 'group': return category, '카타 전국대회 단체전(남자)'

    def _make_competition_category_inner(self, competition_title, result, point):
        category = competition_title[:5]
        if category == '[D그룹]': return 'group'
        txt = result + ':' + point
        if txt in self.POINT_TABLE['open']: return 'open'
        if txt in self.POINT_TABLE['chal']: return 'challenger'
        if txt in self.POINT_TABLE['undecided']:
            if category == '[C그룹]': return 'open'
            if category == '[GA그룹': return 'challenger'
        if txt in self.POINT_TABLE['group']:
            return 'group'
        raise ValueError('result, point is bad: ' + competition_title + ' ' + txt)

    def _make_lt_point(self, result, category):
        # https://en.wikipedia.org/wiki/ATP_Rankings
        # 마스터즈 준용 / 오픈부 기준
        #   W   F   SF  QF  R16 R32 R64 예선통과
        # 1000  600 360 180 90  45  10      2
        OPEN_list = ['카타 전국대회 상급자부(남자)', '카토 전국대회 상급자부(남자)', '생체 전국대회 상급자부(남자)', '기타 랭킹 전국대회 상급자부(남자)', '기타 랭킹 전국대회 신인부(남자)', '지역대회 금배부(남자)', '카타 전국대회 상급자부(여자)', '카토 전국대회 상급자부(여자)', '생체 전국대회 상급자부(여자)', '기타 랭킹 전국대회 상급자부(여자)', '지역대회 금배부(여자)']
        SIN_IN_list = [ '카타 전국대회 신인부(남자)', '카토 전국대회 신인부(남자)', '생체 전국대회 신인부(남자)', '기타 랭킹 전국대회 신인부(남자)', '지역대회 은배부(남자)', '카타 전국대회 신인부(여자)', '카토 전국대회 신인부(여자)', '생체 전국대회 신인부(여자)', '기타 랭킹 전국대회 신인부(여자)', '지역대회 은배부(여자)'
        ]
        GROUP_list = ['카타 전국대회 단체전(남자)']

        점수_1위 = 1000
        점수_2위 = 600
        점수_4강 = 360
        점수_8강 = 180
        점수_16강 = 90
        점수_32강 = 45

        if category in OPEN_list:
            if result == '1위': return 점수_1위
            if result == '2위': return 점수_2위
            if result == '4강': return 점수_4강
            if result == '8강': return 점수_8강
            if result == '16강': return 점수_16강
            if result == '32강': return 점수_32강

        if category in SIN_IN_list:
            if result == '1위': return int(점수_1위 / self.신인부_페널티)
            if result == '2위': return int(점수_2위 / self.신인부_페널티)
            if result == '4강': return int(점수_4강 / self.신인부_페널티)
            if result == '8강': return int(점수_8강 / self.신인부_페널티)
            if result == '16강': return int(점수_16강 / self.신인부_페널티)
            if result == '32강': return int(점수_32강 / self.신인부_페널티)

        if category in GROUP_list:
            if result == '1위': return 200
            if result == '2위': return 140
            if result == '4위' or '4강': return 90
            if result == '8강': return 40
            if result == '16강': return 20
            if result == '32강': return 10


        raise ValueError('그룹이 없습니다: ' + category)




    POINT_TABLE = {
        'open': [
            # 기본요강
            '1위:400', '2위:280', '4강:180', '8강:80', '16강:40', '32강:20', #GA
            '1위:350', '2위:245', '4강:158', '8강:70', '16강:35', '32강:18', #SA
            '1위:300', '2위:210', '4강:135', '8강:60', '16강:30', '32강:15', #A
            '1위:250', '2위:175', '4강:112', '8강:50', '16강:25', '32강:12', #B
            # 변형요강
            '1위:280', '2위:196', '4강:126', '8강:56', '16강:28', '32강:14', #GA
            '1위:245', '2위:172', '4강:111', '8강:49', '16강:25', '32강:13', #SA
            '1위:210', '2위:147', '4강:95', '8강:42', '16강:21', '32강:11', #A
            '1위:175', '2위:123', '4강:78', '8강:35', '16강:18', '32강:8', #B
        ],
        'chal': [
            # 기본요강
            '1위:175', '2위:112', '4강:79', '8강:35', '16강:18', '32강:9', #SA
            '1위:150', '2위:105', '4강:68', '8강:30', '16강:15', '32강:8', #A
            '1위:125', '2위:88', '4강:56', '8강:25', '16강:13', '32강:6',  #B
            '1위:100', '2위:70', '4강:45', '8강:20', '16강:10', '32강:5',  #C,

            # 변형요강
            '1위:123', '2위:78', '4강:55', '8강:26', '16강:13', '32강:6', #SA
            '1위:105', '2위:74', '4강:48', '8강:21', '16강:11', '32강:5', #A
            '1위:88', '2위:62', '4강:39', '8강:18', '16강:9', '32강:4', #B
            '1위:70', '2위:49', '4강:32', '8강:14', '16강:7', '32강:3', #C
        ],
        'undecided': [
            # 오픈부 C와 신인부 GA가 같음
            # 기본요강
            '1위:200', '2위:140', '4강:90', '8강:40', '16강:20', '32강:10',
            # 변형요강
            '1위:140', '2위:98', '4강:63', '8강:28', '16강:14', '32강:7',
        ],
        'group': [
            '1위:70', '2위:49', '4강:32', '8강:14', '16강:7', '32강:3',
            # 규정에 없는 포인트
            # 2019 안양한우리 OPEN
            '1위:50', '2위:35', '4강:23', '8강:10', '16강:5', '32강:3'
        ]
    }