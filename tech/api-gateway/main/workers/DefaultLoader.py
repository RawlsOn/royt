from django.conf import settings
from common.util.romsg import rp

from common.util import juso_util, model_util, str_util
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv, random
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

from common.util import datetime_util, file_util
from django.contrib.gis.geos import Point
from django.apps import apps

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone

from django.contrib.gis.gdal import DataSource, SpatialReference, CoordTransform
from django.contrib.gis.geos import MultiPolygon, Polygon, fromstr
from common.custom.CustomLayerMapping import CustomLayerMapping

pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from common.util.RoPrinter import RoPrinter
PRINT_GAP = 100
printer = RoPrinter('DefaultLoader')
rp = printer.rp
ps = str_util.ProgressShower(gap=PRINT_GAP, info=f'DefaultLoader')
ps.printer = printer

class DefaultLoader(object):

    def __init__(self, args={}):
        self.args = args

    def run(self):
        print('run DefaultLoader')
        ps.info = f'{self.args.baseapp} {self.args.ro_gijun_date} DefaultLoader'
        self.Proto = apps.get_model(f'{self.args.baseapp}proto', 'Proto')
        self.load()

    def load(self):
        print('loading...', self.args.folder_path)

        target_files = glob.glob(os.path.join(
            self.args.folder_path + '/*.shp'
        ))

        files_count = len(target_files)
        pp.pprint(target_files)

        idx = 0
        for target_file in target_files:
            idx += 1
            filename = target_file.split('/')[-1]
            layer_map = CustomLayerMapping(
                model = self.Proto,
                data = target_file,
                # source_srs=SpatialReference(epsg5174),
                # encoding='utf-8',
                encoding=self.args.encoding,
                # transaction_mode='autocommit', # 테스트시
                mapping = {
                    'a0': 'A0',
                    'a1': 'A1',
                    'a2': 'A2',
                    'a3': 'A3',
                    'a4': 'A4',
                    'a5': 'A5',
                    'a6': 'A6',
                    'a7': 'A7',
                    'a8': 'A8',
                    'a9': 'A9',
                    'a10': 'A10',
                    'a11': 'A11',
                    'a12': 'A12',
                    'a13': 'A13',
                    'a14': 'A14',
                    'a15': 'A15',
                    'a16': 'A16',
                    'a17': 'A17',
                    'a18': 'A18',
                    'a19': 'A19',
                    'a20': 'A20',
                    'a21': 'A21',
                    'a22': 'A22',
                    'a23': 'A23',
                    'a24': 'A24',
                    'a25': 'A25',
                    'a26': 'A26',
                    'a27': 'A27',
                    'a28': 'A28',
                    'geom': 'MULTIPOLYGON',
                },
                info = f'{datetime_util.now_str()} {self.args.baseapp} DefaultLoader {idx}/{files_count}: {filename} ',
            )
            # layer_map.save(strict=True, verbose=True)
            layer_map.save(strict=False, verbose=True, step=PRINT_GAP, progress=PRINT_GAP)
            filename_wo_ext = target_file.split('.')[0]
            rp(f'delete files... {filename_wo_ext}')
            file_util.remove_geo_files(filename_wo_ext)
            # file_util.remove_file(filename_wo_ext + '.zip')
