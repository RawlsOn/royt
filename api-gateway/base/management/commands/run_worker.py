from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date, timedelta
import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from django.utils import timezone
from dateutil.relativedelta import relativedelta

import importlib
from django.core.files import File
from argparse import Namespace
import importlib

# ./manage.py run_worker --baseapp=roemail --worker=SendLoginjoinCodeRoMailer
# ./manage.py run_worker --baseapp=roemail --worker=RoMailPreparer

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--worker',
            type=str,
            required=True
        )
        parser.add_argument(
            '--baseapp',
            type=str,
            required=True
        )
        # parser.add_argument(
        #     '--boundaryType',
        #     type=str,
        #     default='Sgg'
        # )
        # parser.add_argument(
        #     '--admin_email',
        #     type=str,
        #     default=settings.ADMIN_EMAIL
        # )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        print(options['worker'])
        module = importlib.import_module(f'{options["baseapp"]}.workers.' + options['worker'])
        worker_loaded = getattr(module, options['worker'])
        worker = worker_loaded(Namespace(**options))
        print(worker)
        worker.run()
