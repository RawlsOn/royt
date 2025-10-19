# 2024-02-17
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
from django.apps import apps

from common.util import juso_util, model_util, str_util, geo_util

from django.core.files import File
from argparse import Namespace

pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from common.util.RoPrinter import RoPrinter
PRINT_GAP = 100
printer = RoPrinter('query_core')
rp = printer.rp
ps = str_util.ProgressShower(gap=PRINT_GAP, info='query_core')
ps.printer = printer

# ./manage.py query_core

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--bbox',
            type=str,
            # default='126.648131,37.439648,126.657467,37.433080'
            # default='127.178346,37.539388,127.217653,37.511127'
            default='127.193100,37.528819,127.202927,37.521753'
        )
        # parser.add_argument(
        #     '--admin_email',
        #     type=str,
        #     default=settings.ADMIN_EMAIL
        # )

    def handle(self, *args, **options):
        """ Do your work here """

        self.bbox = geo_util.bbox_to_polygon(options['bbox'].split(','))
        rp(self.bbox)

        self.Core = apps.get_model('doroggareacore', 'Core')
        self.CoreGrid3 = apps.get_model('doroggareacore', 'Grid3')
        self.Grid3 = apps.get_model('grid3', 'Grid3')
        self.Grid2 = apps.get_model('grid12', 'Grid2')

        # self.query_core()
        self.query_core_with_grid()
        # self.query_grid3()
        # self.query_grid2_from_core()
        # self.query_grid3_from_core()

    def query_core(self):
        rp('query core')
        core_count = self.Core.objects.count()
        rp(f'core_count: {core_count}')

        got = self.Core.objects.filter(geom__intersects=self.bbox)
        rp(got.count())

        # [1.0||query_core|INFO] 2024-02-01_07:16:21 core_count: 7666199

        # [1.0||query_core|INFO] 2024-02-01_07:16:21 POLYGON ((126.648131 37.433080, 126.657467 37.433080, 126.657467 37.439648, 126.648131 37.439648, 126.648131 37.433080))

        # [1.0||query_core|INFO] 2024-02-01_07:18:43 112

        # 766만개 대상 112개 뽑아오는데 2분 20초 걸림 못씀
        # 결국 그리드 만들어서 그리드별로 쿼리해야함

    def query_core_with_grid(self):
        rp('query_core_with_grid')
        # grid2 = self.Grid2.objects.filter(geom__intersects=self.bbox).first()

        core_grid3s = self.CoreGrid3.objects.filter(
            # geom__intersects=grid2.geom,
        ).filter(
            geom__intersects=self.bbox,
        )
        rp(f'CoreGrid3 count {core_grid3s.count()}')

        got = self.Core.objects.filter(
            grid3__in=core_grid3s
        )

        rp(f'Core count {got.count()}')

    def query_grid3(self):
        rp('start query')
        got = self.Grid3.objects.filter(geom__intersects=self.bbox)
        rp(got.count())

    def query_grid3_from_core(self):
        cores = self.Core.objects.all()[:10]
        # core = core[0]
        rp('start query_grid3_from_core')
        rp('query bbox')
        # grids = self.Grid3.objects.filter(geom__intersects=core.bbox)
        # rp(grids.count())

        rp('query bbox')
        for core in cores:
            grids = self.Grid3.objects.filter(geom__intersects=core.bbox)
            print(grids.count())
        rp('end of query bbox')

        rp('query geom')
        for core in cores:
            grids = self.Grid3.objects.filter(geom__intersects=core.geom)
            print(grids.count())
        rp('end of query geom')

    def query_grid2_from_core(self):
        cores = self.Core.objects.all()[:10]
        # core = core[0]
        rp('start query_grid3_from_core')
        rp('query bbox')
        # grids = self.Grid3.objects.filter(geom__intersects=core.bbox)
        # rp(grids.count())

        rp('query bbox')
        for core in cores:
            grid2s = self.Grid2.objects.filter(geom__intersects=core.bbox)
            grid2_ids = list(grid2s.values_list('id', flat=True))
            # rp(f'grid2_ids: {grid2_ids}')
            # print(self.Grid3.objects.first())
            grid3s = self.Grid3.objects.filter(
                grid2__in=grid2_ids,
                geom__intersects=core.bbox
            )
            print(grid3s.count())
            # final = grid3s.filter()
            # print(final.count())

        rp('end of query bbox')

        rp('query geom')
        for core in cores:
            grids = self.Grid2.objects.filter(geom__intersects=core.geom)
            final = grids.filter(geom__intersects=core.bbox)
            print(final.count())
        rp('end of query geom')
