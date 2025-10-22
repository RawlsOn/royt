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
from django.conf import settings

from django.urls import reverse
from django.core.files import File
from tenniscode.workers.SitemapMaker import SitemapMaker

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--base_url',
            type=str,
            default= settings.FE_URL
        )
        parser.add_argument(
            '--target_folder',
            type=str,
            default='/usr/data/tenniscode'
        )

    def handle(self, *args, **options):
        """ Do your work here """

        worker = SitemapMaker(Namespace(**options))
        worker.run()