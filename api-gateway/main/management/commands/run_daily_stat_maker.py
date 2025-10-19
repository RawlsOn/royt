from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date, timedelta
import io, time, os, glob, pprint, json, re, shutil, ntpath
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from common.util.romsg import rp

from argparse import Namespace
from main.workers.DailyStatMaker import DailyStatMaker

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=str,
            default='weekly'
        )
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
        worker = DailyStatMaker(Namespace(**options))
        worker.run()