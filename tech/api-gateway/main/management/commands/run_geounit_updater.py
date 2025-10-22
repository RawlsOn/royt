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
from main.workers.GeoUnitUpdater import GeoUnitUpdater

# ./manage.py run_geounit_updater

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

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        print('run_geounit_updater.py')
        worker = GeoUnitUpdater(Namespace(**options))
        worker.run()
