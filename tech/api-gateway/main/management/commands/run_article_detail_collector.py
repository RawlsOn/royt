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
from main.workers.ArticleDetailCollector import ArticleDetailCollector

# ./manage.py run_article_collector

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--sido',
            type=str,
            default=None
        )
        parser.add_argument(
            '--no',
            type=int,
            default=0
        )
        # parser.add_argument(
        #     '--admin_email',
        #     type=str,
        #     default=settings.ADMIN_EMAIL
        # )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        now = timezone.now()
        # if now.date() >= date(2023, 8, 13) and now.hour >= 9:
        if True:
            if settings.RUN_DETAIL_COLLECTOR:
                worker = ArticleDetailCollector(Namespace(**options))
                worker.run()
            else:
                rp('RUN_DETAIL_COLLECTOR is False, Not running ArticleDetailCollector')
        else:
            rp('not running article detail collector until 2023-08-13 09:00:00')

