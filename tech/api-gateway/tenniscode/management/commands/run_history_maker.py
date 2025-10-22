from dotenv import load_dotenv
load_dotenv(verbose=True)

from argparse import Namespace
import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from datetime import datetime, date, timedelta
from django.utils import timezone
import common.util.datetime_util as datetime_util

from common.util.logger import RoLogger
from common.util.ProgressWatcher import ProgressWatcher
logger = RoLogger()

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from django.urls import reverse
from django.core.files import File
from tenniscode.workers.HistoryMaker import HistoryMaker

# ./manage.py run_history_maker --gijun_date 2022-01-01

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--gijun_date',
            required= True,
            type=lambda x: datetime.strptime(x, "%Y-%m-%d")
        )

    def handle(self, *args, **options):
        """ Do your work here """
        worker = HistoryMaker(Namespace(**options))
        worker.run()