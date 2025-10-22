from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date, timedelta

from common.util.romsg import rp
import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from argparse import Namespace
from main.workers.InstanceWatcher import InstanceWatcher

# ./manage.py run_article_collector

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
        # parser.add_argument(
        #     '--admin_email',
        #     type=str,
        #     default=settings.ADMIN_EMAIL
        # )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        worker = InstanceWatcher(Namespace(**options))
        rp('InstanceWatcher: Starting...')
        while True:
            try:
                worker.stop_instances_running_longer_than_half_an_hour()
                worker.stop_instances_done()
            except Exception as e:
                rp(
                    'InstanceStopper: ' + str(e), msg_type='NOTICE'
                )
                raise e

            rp('InstanceStopper: Sleeping for 87 seconds...')
            time.sleep(87)