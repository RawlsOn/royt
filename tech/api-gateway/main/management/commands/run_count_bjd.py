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
        targets = rawarticle_models.Region.objects.filter(
            regionType= 'emd'
        ).filter(
            Q(sido='경기도')|Q(sido='서울시')|Q(sido='인천시')
        )
        bjd_by_region = [x.sido + ' ' + x.sgg + ' ' + x.title for x in targets]
        bjd_by_region = sorted(bjd_by_region)

        bjd_by_cluster = list(set(
            [x.sido + ' ' + x.sgg + ' ' + x.emd for x in rawarticle_models.Cluster.objects.all()
        ]))
        bjd_by_cluster = sorted(bjd_by_cluster)

        for i in range(len(bjd_by_cluster)-1):
            print(bjd_by_region[i],'\t\t', bjd_by_cluster[i])
            if bjd_by_region[i] != bjd_by_cluster[i]:
                break

        print('region', len(bjd_by_region))

        print('cluster', len(bjd_by_cluster))

        # print(bjd_by_region[-1])