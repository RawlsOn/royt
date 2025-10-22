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

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--loop',
            default=False,
            type=lambda x: (str(x).lower() == 'true')
        )
        parser.add_argument(
            '--sleep_time',
            default=5, # seconds
            type=str
        )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        if self.options['loop']:
            while True:
                self.run()
                logger.INFO('sleep for ' + str(self.options['sleep_time']) + ' seconds...')
                time.sleep(self.options['sleep_time'])
        else:
            self.run()

    def run(self):
        print('sample command')
