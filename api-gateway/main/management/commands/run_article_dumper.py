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
from main.workers.ArticleDumper import ArticleDumper

# ./manage.py run_article_dumper --종류=토지

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--종류',
            type=str,
            required=True
        )
        parser.add_argument(
            '--sido',
            type=str,
            default='서울시'
        )
        # parser.add_argument(
        #     '--admin_email',
        #     type=str,
        #     default=settings.ADMIN_EMAIL
        # )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        worker = ArticleDumper(Namespace(**options))
        worker.run()
