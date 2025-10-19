from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date, timedelta
import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from argparse import Namespace
from main.workers.ArticleDetailProcessor import ArticleDetailProcessor
import core.models as core_models
from django.apps import apps
from main.workers.ArticleDetailProcessor import ArticleDetailProcessor

# ./manage.py fix_article_detail --sido=서울시

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--sido',
            type=str,
            required=True
        )
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
        LIMIT = 10000
        self.options = options
        worker = ArticleDetailProcessor(Namespace(**options))
        sido = self.options['sido']
        model = apps.get_model('core', 'Article' + sido)
        QUERY = f"""
SELECT * FROM core_article{sido}
WHERE is_detail_processed= 1
    and is_detail_failed= 0
    and PNU IS NULL
LIMIT {LIMIT} OFFSET {LIMIT * self.options['no']};
"""

        print(QUERY)
        targets = model.objects.raw(QUERY)
        worker.idx = 1
        worker.total_count = LIMIT
        worker.model = model
        for target in targets:
            # print(target, target.종류, target.detail_processed_at, target.juso)
            # print('start process')
            worker._process(target)
            # print(target, target.detail_processed_at)
