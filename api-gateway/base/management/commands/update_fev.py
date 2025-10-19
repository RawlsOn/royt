import base.models as base_models
from django.core.files import File
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError
from common.util.ProgressWatcher import ProgressWatcher
from common.util.logger import RoLogger
from django.utils import timezone
from datetime import datetime, date, timedelta
import io
import time
import os
import glob
import pprint
import json
import re
import shutil
import ntpath
pp = pprint.PrettyPrinter(indent=2)  # pp.pprint()
logger = RoLogger()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--note',
            required=False,  # seconds
            type=str
        )
        parser.add_argument(
            '--loop',
            default=False,
            type=lambda x: (str(x).lower() == 'true')
        )
        parser.add_argument(
            '--sleep_time',
            default=5,  # seconds
            type=str
        )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        if self.options['loop']:
            while True:
                self.run()
                logger.INFO('sleep for ' +
                            str(self.options['sleep_time']) + ' seconds...')
                time.sleep(self.options['sleep_time'])
        else:
            self.run()

    def run(self):
        print('update_fe_version')
        if self.options['note'] is None:
            self.options['note'] = ''
        base_models.FrontendVersion.objects.create(**{
            'note': self.options['note']
        })
