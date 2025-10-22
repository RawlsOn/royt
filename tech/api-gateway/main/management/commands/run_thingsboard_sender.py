from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date, timedelta
import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from common.util.romsg import rp

from argparse import Namespace
from main.workers.ThingsboardSender import ThingsboardSender
import config.models as config_models

# ./manage.py run_thingsboard_sender

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--base_url',
            type=str,
            default='http://thingsboard:9090'
        )
        parser.add_argument(
            '--device_token',
            type=str,
            default=''
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=10 # minutes
        )
        # parser.add_argument(
        #     '--upload_day',
        #     type=str,
        #     default='01'
        # )
        # parser.add_argument(
        #     '--admin_email',
        #     type=str,
        #     default=settings.ADMIN_EMAIL
        # )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        rp('Wait until thingsboard is ready...')
        rp('Wait for 2 minutes...')
        # 따로 체크할 방법은 없고 그냥 2분 있다가 시작함
        time.sleep(120)
        worker = ThingsboardSender(Namespace(**options))
        worker.run()