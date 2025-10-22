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
import history.models as history_models

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

class HistoryMaker(object):

    def __init__(self, args={}):
        self.args = args
        self.기준일 = self.args.gijun_date

    def run(self):
        print('run HistoryMaker', self.args)

        idx = 0
        targets = tenniscode_models.Club.objects.all()
        total = targets.count()

        for club in targets:
            idx += 1
            str_util.print_progress(idx, total, gap=10, info='make club history')
            club_obj = club.to_obj
            del club_obj['prev_full_rank']
            del club_obj['prev_challenger_rank']
            del club_obj['prev_master_rank']
            del club_obj['id']
            club_obj['기준일str'] = club.기준일.strftime('%Y-%m-%d')

            history_models.ClubHistory.objects.get_or_create(
                title= club.title,
                기준일= club.기준일,
                defaults= club_obj
            )

        idx = 0
        targets = tenniscode_models.Player.objects.all()
        total = targets.count()

        for player in targets:
            idx += 1
            str_util.print_progress(idx, total, gap=10, info='make player history')
            player_obj = player.to_obj
            del player_obj['prev_rank']
            del player_obj['id']
            player_obj['기준일str'] = player.기준일.strftime('%Y-%m-%d')
            history_models.PlayerHistory.objects.get_or_create(
                name= player.name,
                기준일= player.기준일,
                defaults= player_obj
            )



