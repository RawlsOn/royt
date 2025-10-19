# 2024-02-25
# cp /Users/kimmyounghoon/Works/mkay/common/api-gateway/main/management/commands/* ./api-gateway/main/management/commands/

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date, timedelta
import io, time, os, glob, pprint, json, re, shutil, ntpath, random
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from django.core.files import File
from argparse import Namespace

from django.apps import apps

# ./manage.py show_proto --app=dorohhproto

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--show_samples',
            default=False,
            type=lambda x: (str(x).lower() == 'true')
        )

        parser.add_argument(
            '--app',
            type=str,
            required=True
        )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options

        model = apps.get_model(options['app'], 'proto')

        print('count', model.objects.count())
        pp.pprint(model.objects.first().all_prop)
        pp.pprint(model.objects.first().data_to_core())

        if options['show_samples']:
            print('querying for show_samples')
            ids = list(model.objects.all().values_list('id', flat=True))
            random.shuffle(ids)
            ids = ids[:100]
            for id in ids:
                print('core id', model.objects.get(id=id).data_to_core()['id'])



        # results = model.objects.filter(
        #     present_sn= '29140UQ151PS201305091382'
        # )
        # for result in results:
        #     pp.pprint(result.all_prop)
        #     print(result.geom)