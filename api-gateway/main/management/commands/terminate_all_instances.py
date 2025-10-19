from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date, timedelta
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from common.util import juso_util, model_util, str_util

from django.core.files import File
from argparse import Namespace
from main.workers.InstanceMonitor import InstanceMonitor 

# ./manage.py show_instances
class Command(BaseCommand):

    def add_arguments(self, parser):
        pass
        # parser.add_argument(
        #     '--single',
        #     default=False,
        #     type=lambda x: (str(x).lower() == 'true')
        # )
        # parser.add_argument(
        #     '--juso',
        #     required= False,
        #     type= str
        # )

        # parser.add_argument(
        #     '--file_path',
        #     type=str,
        #     required=False
        # )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        worker = InstanceMonitor(Namespace(**options))
        worker.show_instances()
        worker.terminate_all_instances()