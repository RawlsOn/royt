from django.conf import settings
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
import geoinfo.models as geoinfo_models

# ./manage.py run_load_bjd_emd --file_path=/usr/data/robasev2-local/bjd_emd_20221031_utf8.csv
# ./manage.py run_load_bjd_emd --single=true --juso="인천광역시 서구 가좌동"

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--single',
            default=False,
            type=lambda x: (str(x).lower() == 'true')
        )
        parser.add_argument(
            '--juso',
            required= False,
            type= str
        )

        parser.add_argument(
            '--file_path',
            type=str,
            required=False
        )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        print('run_load_emd')
        if options['single']:
            if not options['juso']:
                raise ValueError('주소가 필요합니다. : --juso=:"인천광역시 서구 가좌동"')
            self.do_job(options['juso'])
        else:
            # self.load()
            self.make_json_of_emd()

    def make_json_of_emd(self):
        print('make_json_of_emd')
        targets = geoinfo_models.GeoUnit.objects.filter(geo_type='SECTOR')
        print(targets.count())
        with open('/usr/data/robasev2-local/230619_emd.json', 'w') as f:
            to_write_total = []
            for target in targets:
                to_write = {
                    'center_x': target.center_x,
                    'center_y': target.center_y,
                    '지번주소': target.지번주소,
                    '읍면동': target.읍면동
                }
                to_write_total.append(to_write)
            f.write(json.dumps(to_write_total, ensure_ascii=False))

    def load(self):
        with open(self.options['file_path'], 'r') as f:
            total_count = 46330
            csvreader = csv.reader(f)
            idx = 0
            for row in csvreader:
                idx += 1
                if idx == 1:
                    continue

                if row[1] in [
                    '강원도',
                    '충청남도', '충청북도',
                    '대구광역시', '대구직할시',
                    '부산광역시', '부산직할시',
                    '전라북도', '전라남도',
                    '대전광역시', '대전직할시',
                    '광주광역시', '광주직할시',
                    '세종특별자치시',
                    '부산광역시', '부산직할시',
                    '경상북도', '경상남도',
                    '제주특별자치도', '제주도'
                ]:
                    continue
                juso = ' '.join(row[1:5])
                deleted_date = row[7]
                if deleted_date.strip() != '':
                    continue
                self.do_job(juso)
                # break
                # self.do_job(row[4])
            #     # if idx > 2: break
            #         str_util.print_progress(idx, total_count, gap= 10, info='create geounit...')
            # # print(idx)

    def do_job(self, juso):
        print('do_job:', juso)
        geo_unit = model_util.get_or_none(geoinfo_models.GeoUnit, 주소_input= juso)
        if geo_unit:
            print('already done: ', geo_unit)
            return

        k_juso_obj, success = juso_util.get_kakao_juso(juso)
        time.sleep(1)
        if success:
            geo_unit, created = geoinfo_models.GeoUnit.objects.get_or_create(
                주소_input= juso.strip(),
                uniq_title= k_juso_obj['지번주소'],
                defaults= {
                    '지번주소': k_juso_obj['지번주소'],
                    '도로명주소': k_juso_obj['도로명주소'],
                    '시도': k_juso_obj['시도'],
                    '시군구': k_juso_obj['시군구'],
                    '읍면동': k_juso_obj['읍면동'],
                    'point': k_juso_obj['point'],
                    'center': k_juso_obj['center'],
                    'geo_type': 'SECTOR'
                }
            )
