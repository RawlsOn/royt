from dotenv import load_dotenv
load_dotenv(verbose=True)
from django.conf import settings

import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from datetime import datetime, date, timedelta
from django.utils import timezone
from common.util.logger import RoLogger
from common.util.ProgressWatcher import ProgressWatcher
logger = RoLogger()

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import Group
from django.urls import reverse
from django.core.files import File
from django.contrib.auth import get_user_model
import main.models as main_models
import config.models as config_models

from random import randrange

class Command(BaseCommand):

    def add_arguments(self, parser):
        pass
        # parser.add_argument(
        #     '--dump',
        #     type=bool,
        #     default=False
        # )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        # self.add_sample_users()
        User = get_user_model()
        User.objects.all().delete()
        User.objects.create_superuser('admin', 'admin@admin.com', 'admin')

        self.create_config_funding_msg()

    def create_config_funding_msg(self):
        msgs = [
            [0,  'AI 감정가가 없습니다. 펀딩 신청을 남겨주시면 별도 연락드리겠습니다.', '😯'],
            [10,  '투자 펀딩이 불가할 수도 있어요. 심사를 요청해주세요~!', '😯'],
            [20,  '투자 펀딩에 어려운 조건이 될 수 있어요. 상환기간을 낮추고 투자자 지급 이자를 높여야 할 수도 있어요~!', '😯'],
            [30,  '투자 펀딩에 조금은 어려운 조건이에요. 성공적인 펀딩을 위해선 상환기간을 줄여야 할 수도 있어요~!', '😯'],
            [40,  '투자 펀딩에 나쁘지 않은 조건 이에요. 빠른 펀딩을 위해서 상환기간을 줄여야 할 수도 있어요~!', '😯'],
            [50,  '투자 펀딩에 보통의 조건이에요. 상환기간을 줄이면 더 빠른 펀딩이 될 수도 있어요~!', '😯'],
            [60,  '투자 펀딩에 적당한 조건이에요. 투자자분들이 무난하게 참여하실 거예요!', '😮'],
            [70,  '투자 펀딩에 좋은 조건입니다. 많은 투자자분들이 참여하실 거예요!', '😐'],
            [80,  '투자 펀딩에 좋은 조건입니다. 많은 투자자분들이 참여하실 거예요!', '🙂'],
            [85,  '투자 펀딩에 좋은 조건입니다. 많은 투자자분들이 참여하실 거예요!', '😄'],
            [90,  '투자 펀딩에 매우 좋은 조건입니다. 지금 바로 신청하세요!', '😊'],
            [95,  '투자 펀딩에 매우 좋은 조건입니다. 지금 바로 신청하세요!', '🤗'],
            [100, '투자 펀딩에 매우 좋은 조건입니다. 지금 바로 신청하세요!', '😍']
        ]
        for datum in msgs:
            config_models.FundingMsg.objects.create(**{
                'score': datum[0],
                'msg': datum[1],
                'emoji': datum[2]
            })