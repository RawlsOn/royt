from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date, timedelta
import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import rawarticle.models as rawarticle_models

from argparse import Namespace

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
        found = rawarticle_models.RegionInstanceMap.objects.filter(instance_id= settings.EC2_INSTANCE_ID).first()
        if found:
            print('Instance already registered:' + settings.EC2_INSTANCE_ID)
        else:
            rawarticle_models.RegionInstanceMap.objects.create(
                instance_id= settings.EC2_INSTANCE_ID,
                region= settings.REGION_TARGETS[0],
                aws_region= settings.EC2_AWS_REGION,
                state= 'running',
                launch_time= timezone.now(),
            )
