# 2024-02-25
# cp /Users/kimmyounghoon/Works/mkay/common/api-gateway/main/management/commands/* ./api-gateway/main/management/commands/

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
from main.workers.CoreIndexer import CoreIndexer

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--baseapp',
            type=str,
            required=True
        )
        # parser.add_argument(
        #     '--folder_path',
        #     type=str,
        #     required=True
        # )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        worker = CoreIndexer(Namespace(**options))
        worker.run()
