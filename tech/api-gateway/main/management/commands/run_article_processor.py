from django.conf import settings
from common.util.romsg import rp
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date, timedelta
import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from django.core.files import File
from argparse import Namespace
from main.workers.ArticleProcessor import ArticleProcessor

# ./manage.py run_article_processor --no=0
# ./manage.py run_article_processor --no=1
# ./manage.py run_article_processor --no=2
# ./manage.py run_article_processor --no=3

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--no',
            type=int,
            default=0
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
        while True:
            try:
                worker = ArticleProcessor(Namespace(**options))
                worker.run()
            except Exception as e:
                print(str(e))
                if 'Server has gone away' in str(e):
                    rp('Wait 1 min')
                    time.sleep(60)
                    return
                rp('Wait 1 min')
                time.sleep(60)