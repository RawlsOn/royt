from django.conf import settings
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
from main.workers.ExcelLoader import ExcelLoader
from main.workers.PostProcessExcelLoader import PostProcessExcelLoader

# docker exec robasev2-api-gateway-1 ./manage.py run_excel_loader --file_path=/usr/data/robasev2-local/upload/2baea8fb-a13b-4f20-a148-52457ca6e320.xlsx

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--file_path',
            type=str,
            required=True
        )
        parser.add_argument(
            '--upload_day',
            type=str,
            default='01'
        )
        parser.add_argument(
            '--admin_email',
            type=str,
            default=settings.ADMIN_EMAIL
        )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        print('run_excel_loader.py')
        loader = ExcelLoader(Namespace(**options))
        loader.run()

        worker = PostProcessExcelLoader(Namespace(**options))
        worker.run()