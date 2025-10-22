from dotenv import load_dotenv
load_dotenv(verbose=True)

import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
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
from common.util import api_util, str_util
from tenniscode.workers.ImageMaker import ImageMaker

# ./manage.py run_image_maker --text='클럽랭킹'

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--text',
            required=False,
            type=str
        )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        self.run()

    def run(self):
        print('run')

        self.im = ImageMaker()
        print(self.options['text'])
        if self.options['text'] is not None:
            self.im.run(self.options['text'])
        else:
            self.make()

    def make(self):
        total_count = raw_data_models.Club.objects.count()
        idx = 0
        for club in raw_data_models.Club.objects.all():
            idx += 1
            str_util.print_progress(idx, total_count, gap= 100, info='clubs...')
            self.im.run(club.title)
