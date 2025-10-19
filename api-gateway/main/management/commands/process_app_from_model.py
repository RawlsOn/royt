from dotenv import load_dotenv
load_dotenv(verbose=True)

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

from django.urls import reverse
from django.core.files import File

from common.util.app_processor import AppProcessor
from argparse import Namespace

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--loop',
            default=False,
            type=lambda x: (str(x).lower() == 'true')
        )
        parser.add_argument(
            '--app_name',
            default='config',
            type=str
        )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        ap = AppProcessor(Namespace(**self.options))
        ap.run()