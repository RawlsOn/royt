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

from django.apps import apps

# ./manage.py test_rojijeok --api='/api/rojijeokcore/core/1168010800100850014/'

class Command(BaseCommand):

    def add_arguments(self, parser):
        # parser.add_argument(
        #     '--is_test',
        #     default=False,
        #     type=lambda x: (str(x).lower() == 'true')
        # )

        parser.add_argument(
            '--api',
            type=str,
            required=True
        )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options

        model = apps.get_model(options['app'], 'core')

        if options['id'] is None:
            pp.pprint(model.objects.last().all_prop)
            return

        pp.pprint(model.objects.get(id=options['id']).all_prop)
        # print(model.objects.get(id=options['id']).geom)

# { '_state': <django.db.models.base.ModelState object at 0xffff9ddd4950>,
#   'atrb_se': 'UQS122',
#   'create_dat': datetime.date(2013, 5, 8),
#   'created_at': datetime.datetime(2024, 2, 18, 18, 48, 12, 766753),
#   'created_date': datetime.date(2024, 2, 18),
#   'dgm_ar': 345.0,
#   'dgm_lt': 131.0,
#   'dgm_nm': '소로3류',
#   'drawing_no': None,
#   'excut_se': 'EMA0001',
#   'gijun_date': datetime.date(2024, 1, 13),
#   'gijun_date_str': '2024-01-13',
#   'grad_se': '소로',
#   'history': [],
#   'id': '29140UQ151PS201305091382_None_2013-05-08',
#   'is_indexed': False,
#   'lclas_cl': 'UQS122',
#   'mlsfc_cl': None,
#   'ntfc_sn': None,
#   'present_sn': '29140UQ151PS201305091382',
#   'road_no': None,
#   'road_role': None,
#   'road_ty': '3',
#   'sclas_cl': None,
#   'signgu_se': '29000',
#   'updated_at': datetime.datetime(2024, 2, 18, 18, 48, 12, 766760),
#   'wtnnc_sn': '29000URZ999999999999'}