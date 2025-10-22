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

class ClubRankingMaker(object):
    def __init__(self, args={}):
        pass

    def run(self):
        print('run ClubRankingMaker')

        self.sum_points()
        self.make_ranking()

    def sum_points(self):
        idx = 0
        targets = tenniscode_models.Club.objects.all()
        total = targets.count()
        for club in targets:
            idx += 1
            str_util.print_progress(idx, total, gap=10, info='sum point')
            club.kata_point = 0
            club.point = 0
            club.challenger_point = 0

            players = tenniscode_models.Player.objects.filter(
                clubs__in= [club.id]
            )

            for player in players:
                club.kata_point += player.kata_point
                club.point += player.point

                if player.player_level == '신인부(남자)':
                    club.challenger_point += player.point

            club.save()

    def make_ranking(self):
        total = tenniscode_models.Club.objects.all().count()
        for idx, club in enumerate(tenniscode_models.Club.objects.all().order_by('-point')):
            str_util.print_progress(idx, total, 'make club ranking')
            club.rank = idx + 1
            club.save()

        for idx, club in enumerate(tenniscode_models.Club.objects.all().order_by('-challenger_point')):
            str_util.print_progress(idx, total, 'make chal club ranking')
            club.challenger_rank = idx + 1
            club.save()