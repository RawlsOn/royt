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

from dateutil.relativedelta import relativedelta
import tenniscode.models as tenniscode_models
import history.models as history_models

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# ./manage.py run_updater

class Updater(object):
    def __init__(self, args={}):
        self.args = args

    def run(self):
        self.make_player()
        self.make_club()

    def make_player(self):
        targets = history_models.PlayerPrepared.objects.all()
        total = targets.count()
        for idx, pp in enumerate(targets):
            str_util.print_progress(idx, total, 'update player')
            player = tenniscode_models.Player.objects.get(
                name= pp.name,
                main_club_str= pp.main_club_str
            )
            player.prev_rank = player.rank
            player.rank = pp.rank

            player.full_point = pp.full_point
            player.master_point = pp.master_point
            player.challenger_point = pp.challenger_point

            player.player_level = pp.player_level
            player.기준일 = pp.기준일
            player.기준일str = pp.기준일.strftime('%Y-%m-%d')

            player.save()

    def make_club(self):
        targets = history_models.ClubPrepared.objects.all()
        total = targets.count()
        for idx, cc in enumerate(targets):
            str_util.print_progress(idx, total, 'update club')
            club = tenniscode_models.Club.objects.get(
                title= cc.title
            )
            club.full_point = cc.full_point
            club.master_point = cc.master_point
            club.challenger_point = cc.challenger_point

            club.prev_full_rank = club.full_rank
            club.prev_master_rank = club.master_rank
            club.prev_challenger_rank = club.challenger_rank

            club.full_rank = cc.full_rank
            club.master_rank = cc.master_rank
            club.challenger_rank = cc.challenger_rank

            club.players_count_having_performance = cc.players_count_having_performance

            club.기준일 = cc.기준일
            club.기준일str = cc.기준일.strftime('%Y-%m-%d')
            club.save()
