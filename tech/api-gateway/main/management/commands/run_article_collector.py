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
from main.workers.ArticleCollector import ArticleCollector
import config.models as config_models

# ./manage.py run_article_collector

class Command(BaseCommand):

    def add_arguments(self, parser):
        pass
        # parser.add_argument(
        #     '--file_path',
        #     type=str,
        #     required=True
        # )
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
        # AMI를 만들기 위한 패치
        # AMI만들 때 crontab에 1분마다 콜렉터가 돌아가는지 아는지 체크하는 것을 넣는데
        # 이미지를 굽기 전에 이게 돌아가 버려서
        # 프로세스가 뜬 채로 구워짐
        # 그래서 30분정도 텀을 둬서 구워질 때는 프로세스가 안 뜨게 하고
        # 구워진 게 나중에 인스턴스가 될 때는 크론탭으로 신규소스코드로 띄울 수 있게 함
        # 지금 8시 30분이니까 9시 이후부터 돌아가도록 해야 함
        if config_models.Setting.objects.last().is_list_collector_runnable:
            worker = ArticleCollector(Namespace(**options))
            worker.run()

        # now = timezone.now()
        # print(now.date(), date(2023, 8, 13))
        # print('now.date() >= date(2023, 8, 13)', now.date() >= date(2023, 8, 13))
        # if now.date() >= date(2023, 8, 13) and now.hour >= 9:
        #     else:
        #         rp('is_list_collector_runnable is False, Not running ArticleCollector')
        # else:
        #     rp('not running article collector until 2023-08-13 09:00:00')
