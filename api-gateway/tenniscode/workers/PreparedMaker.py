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

# ./manage.py run_prepared_maker

PLUS_POINT_PER_PLAYER = 100

class PreparedMaker(object):
    def __init__(self, args={}):
        self.args = args

    def run(self):
        print('run PreparedMaker')
        self.make_player_prepared()
        self.make_club_prepared()
        self.make_player_ranking()
        self.make_club_ranking()

    def make_player_prepared(self):
        print('delete PlayerPrepared...')
        history_models.PlayerPrepared.objects.all().delete()

        idx = 0
        targets = tenniscode_models.Player.objects.all()
        # targets = tenniscode_models.Player.objects.filter(name= '노재승')

        total = targets.count()
        for player in targets:
            player_obj = player.to_obj
            del player_obj['prev_rank']
            player_prepared = history_models.PlayerPrepared.objects.create(**player_obj)
            idx += 1
            str_util.print_progress(idx, total, 'sum player point')
            player_prepared.point = 0
            player_prepared.master_point = 0
            player_prepared.challenger_point = 0

            queryset = tenniscode_models.Performance.objects.filter(player= player)
            queryset.update(is_effective= False)

            performances = queryset.filter(
                match_date__gte= self.args.gijun_date - relativedelta(years=1)
            )

            for performance in performances:
                if performance.performance_level == '상급자부(남자)':
                    player_prepared.master_point += performance.point
                    # performance.is_effective = True
                    # performance.save()
                elif performance.performance_level == '신인부(남자)':
                    player_prepared.challenger_point += performance.point
                    # performance.is_effective = True
                    # performance.save()
                else:
                    raise ValueError('bad performance.performance_level: ' + performance.performance_level)

            player_prepared.기준일 = self.args.gijun_date


            player_prepared.full_point = player_prepared.master_point + player_prepared.challenger_point

            player_prepared.save()

    def make_club_prepared(self):
        print('delete ClubPrepared')
        history_models.ClubPrepared.objects.all().delete()
        idx = 0
        targets = tenniscode_models.Club.objects.all()
        total = targets.count()

        for club in targets:
            club_obj = club.to_obj
            del club_obj['prev_full_rank']
            del club_obj['prev_master_rank']
            del club_obj['prev_challenger_rank']
            club_prepared = history_models.ClubPrepared.objects.create(**club_obj)
            idx += 1
            str_util.print_progress(idx, total, 'sum club point')

            club_prepared.full_point = 0
            club_prepared.master_point = 0
            club_prepared.challenger_point = 0

            players = tenniscode_models.Player.objects.filter(
                clubs__in= [club.id]
            )

            players_count_having_performance = 0

            for player in players:
                player_prepared = history_models.PlayerPrepared.objects.get(name= player.name, main_club_str= player.main_club_str)

                if player_prepared.master_point != 0 or player_prepared.challenger_point != 0:
                    players_count_having_performance += 1

                club_prepared.master_point += player_prepared.master_point
                club_prepared.challenger_point += player_prepared.challenger_point
                club_prepared.full_point += player_prepared.full_point

            # print('players_count_having_performance', players_count_having_performance, club)
            # print('BEFORE', club_prepared.master_point, club_prepared.challenger_point, club_prepared.full_point)

            club_prepared.master_point += PLUS_POINT_PER_PLAYER * players_count_having_performance
            club_prepared.challenger_point += PLUS_POINT_PER_PLAYER * players_count_having_performance
            club_prepared.full_point += PLUS_POINT_PER_PLAYER * players_count_having_performance

            club_prepared.players_count_having_performance = players_count_having_performance

            # print('AFTER', club_prepared.master_point, club_prepared.challenger_point, club_prepared.full_point)

            club_prepared.기준일 = self.args.gijun_date
            club_prepared.save()

            # pp.pprint(club_prepared.to_obj)

    def make_player_ranking(self):
        print('make player ranking...')

        상급자부_남자s = history_models.PlayerPrepared.objects.filter(
            player_level= '상급자부(남자)'
        ).order_by('-master_point')
        total = 상급자부_남자s.count()
        previous_player_point = None
        gap = 1
        rank = 0
        idx = 0
        for player in 상급자부_남자s:
            str_util.print_progress(idx, total, 'make player 상급자부(남자) ranking')
            if previous_player_point == player.master_point:
                player.rank = rank
                gap += 1
            else:
                rank += gap
                player.rank = rank
                previous_player_point = player.master_point
                gap = 1
            player.save()
            idx += 1

        신인부_남자s = history_models.PlayerPrepared.objects.filter(
            player_level= '신인부(남자)'
        ).order_by('-full_point')
        total = 신인부_남자s.count()
        previous_player_point = None
        gap = 1
        rank = 0
        idx = 0
        for player in 신인부_남자s:
            str_util.print_progress(idx, total, 'make player 신인부(남자) ranking')
            if previous_player_point == player.full_point:
                player.rank = rank
                gap += 1
            else:
                rank += gap
                player.rank = rank
                previous_player_point = player.full_point
                gap = 1
            player.save()
            idx += 1


    def make_club_ranking(self):
        print('make club ranking...')
        total = history_models.ClubPrepared.objects.all().count()
        previous_club_point = None
        gap = 1
        rank = 0
        idx = 0
        for club in history_models.ClubPrepared.objects.all().order_by('-full_point'):
            if previous_club_point == club.full_point:
                club.full_rank = rank
                gap += 1
            else:
                rank += gap
                club.full_rank = rank
                previous_club_point = club.full_point
                gap = 1
            print('통합', club.full_rank, club.full_point, club.title)
            club.save()
            idx += 1


        previous_club_point = None
        gap = 1
        rank = 0
        idx = 0
        for club in history_models.ClubPrepared.objects.all().order_by('-master_point'):
            if previous_club_point == club.master_point:
                club.master_rank = rank
                gap += 1
            else:
                rank += gap
                club.master_rank = rank
                previous_club_point = club.master_point
                gap = 1
            print('마스터', club.master_rank, club.master_point, club.title)
            club.save()
            idx += 1


        previous_club_point = None
        gap = 1
        rank = 0
        idx = 0
        for club in history_models.ClubPrepared.objects.all().order_by('-challenger_point'):
            if previous_club_point == club.challenger_point:
                club.challenger_rank = rank
                gap += 1
            else:
                rank += gap
                club.challenger_rank = rank
                previous_club_point = club.challenger_point
                gap = 1
            print('신인', club.challenger_rank, club.challenger_point, club.title)
            club.save()
            idx += 1
