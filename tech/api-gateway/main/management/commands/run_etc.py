from django.conf import settings

from common.util.romsg import rp
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
import rawarticle.models as rawarticle_models

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
        while True:
            rp('keep full 1 instance')
            TC = rawarticle_models.ArticleCollectorTargetCount
            last =TC.objects.last()
            print(last.us_east_1, last.us_east_2)
            if not (last.us_east_1 == 1 and last.us_east_2 == 1):
                TC.objects.create(
                    us_east_1 = 1,
                    us_east_2 = 1,
                    us_west_1 = 1,
                    us_west_2 = 1,
                    af_south_1 = 1,
                    ap_east_1 = 1,
                    ap_south_2 = 1,
                    ap_southeast_3 = 1,
                    ap_southeast_4 = 1,
                    ap_south_1 = 1,
                    ap_northeast_3 = 1,
                    ap_southeast_1 = 1,
                    ap_southeast_2 = 1,
                    ap_northeast_1 = 1,
                    ca_central_1 = 1,
                    eu_central_1 = 1,
                    eu_west_1 = 1,
                    eu_west_2 = 1,
                    eu_south_1 = 1,
                    eu_west_3 = 1,
                    eu_south_2 = 1,
                    eu_north_1 = 1,
                    sa_east_1 = 1,
                )
            time.sleep(10)# worker.show_instances()