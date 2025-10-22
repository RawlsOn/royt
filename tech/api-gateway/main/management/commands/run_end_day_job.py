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

from argparse import Namespace
import rawarticle.models as rawarticle_models

# ./manage.py run_end_day_job

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
        self.delete_old()

    def delete_old(self):
        print('오늘 전에 생성된 protoarticle 삭제')
        targets = rawarticle_models.ProtoArticle.objects.filter(
            created_date__lt=timezone.now().date()
        ).all()

        print(targets.count())
        if targets.count() > 0:
            print('deleting...')
            targets.delete()