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

# ./manage.py run_cluster_lgeo_check --lgeo=21212101

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--lgeo',
            type=str,
            required=True
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
        print('counting...')
        count = rawarticle_models.ProtoArticle.objects.filter(
            lgeo=options['lgeo'],
            created_date__gte=timezone.now().date()
        ).count()
        clusters = rawarticle_models.Cluster.objects.filter(
            lgeo=options['lgeo']
        ).all()
        print('article count', count)
        for cluster in clusters:
            print(cluster.sido, cluster.sgg, cluster.emd, cluster.lgeo, cluster.count)