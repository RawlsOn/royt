from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date, timedelta

from common.util.romsg import rp
import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from dateutil.relativedelta import relativedelta

from argparse import Namespace
import rawarticle.models as rawarticle_models
from common.util import aws_util, str_util

# ./manage.py update_region

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

        #############
        # 처음 돌릴 때는 Region의 모든 is_updated를 False로 바꾸고 시작할 것
        # 생각보다 중간에 에러가 나는 게 있어서 상태관리를 해줘야 함
        emds = rawarticle_models.Region.objects.filter(
            regionType= 'emd',
            is_updated= False
        )
        total = emds.count()
        while total > 0:
            for idx, emd in enumerate(emds):
                str_util.print_progress(
                    idx, total,
                    emd.sido + ' ' + emd.sgg + ' ' + emd.title,
                    gap=1
                )
                emd_obj = emd.to_obj
                del emd_obj['created_date']
                del emd_obj['created_at']
                del emd_obj['updated_at']
                del emd_obj['update_start_time']
                del emd_obj['update_end_time']

                local_folder = '/usr/data/onenaverlandcrawler-local/tmp'
                file_name = 'meta.json'
                with open(local_folder + '/' + file_name, 'w') as f:
                    f.write(json.dumps(emd_obj, ensure_ascii=False, indent=2))
                aws_util.upload_file(
                    local_folder,
                    file_name,
                    '/'.join([
                        'ro-nogit-data/landn',
                        emd.sido,
                        emd.sgg,
                        emd.title,
                        file_name
                    ])
                )
                emd.is_updated = True
                emd.save()

