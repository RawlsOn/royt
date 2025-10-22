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
import rawarticle.models as rawarticle_models
import monitoring.models as m_models
from main.workers.JobMonitor import JobMonitor

# ./manage.py run_job_monitor
# ./manage.py run_job_monitor --run_type=detail

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--run_type',
            type=str,
            default='default'
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
        worker = JobMonitor(Namespace(**options))

        while True:

            if options['run_type'] == 'default':
                worker.run()

            # if options['run_type'] == 'detail':
            #     worker.run_detail()
            #     return


            elif options['run_type'] == 'proto':
                worker.run_proto()

            elif options['run_type'] == 'all':
                worker.run()
                worker.run_proto()

            rp('Sleeping 60 seconds...')
            time.sleep(60)
