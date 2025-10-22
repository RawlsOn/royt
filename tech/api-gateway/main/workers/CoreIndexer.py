# 2024-02-26
# cp /Users/kimmyounghoon/Works/mkay/common/api-gateway/main/workers/CoreIndexer.py ./api-gateway/main/workers/

# ./manage.py run_core_indexer --baseapp=jijeok

from django.conf import settings
from common.util.romsg import rp

from common.util import juso_util, model_util, str_util, geo_util
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv, random
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

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

# http://localhost:4115/api/ydjycore/core/?in_bbox=126.497177,37.588832,127.535139,36.981752

class CoreIndexer(object):

    def __init__(self, args={}):
        printer = RoPrinter(f'{args.baseapp} Indexer')
        self.rp = printer.rp
        self.ps = str_util.ProgressShower(gap=PRINT_GAP, info=f'{args.baseapp}Indexer')
        self.ps.printer = printer
        self.args = args

    def run(self):
        print(f'{self.args.baseapp}Indexer')
        self.make_index()

    def make_index(self):
        self.rp('make_index')

        OriginalGrid2 = apps.get_model('grid12', 'Grid2')
        OriginalGrid3 = apps.get_model('grid3', 'Grid3')

        TargetGrid3 = apps.get_model(f'{self.args.baseapp}core', 'Grid3')


        Core = apps.get_model(f'{self.args.baseapp}core', 'Core')

        # print('reset')
        # Core.objects.update(is_indexed= False)
        # TargetGrid3.objects.all().delete()

        core_ids = Core.objects.filter(is_indexed= False).values_list('id', flat=True)

        self.ps.total = core_ids.count()
        self.rp(f'core_ids count {self.ps.total}')
        self.rp(f'grid3 count {TargetGrid3.objects.count()}')

        for core_id in core_ids:
            core = Core.objects.get(id=core_id)
            self.ps.show()
            grid2s = OriginalGrid2.objects.filter(geom__intersects=core.geom)
            for grid2 in grid2s:

                o_grid3s = OriginalGrid3.objects.filter(
                    grid2=grid2.id,
                    geom__intersects=core.geom
                )
                for o_grid3 in o_grid3s:
                    t_grid3, created = TargetGrid3.objects.get_or_create(
                        id= o_grid3.id,
                        defaults= dict(
                            geom=o_grid3.geom,
                            grid2_id=grid2.id
                        )
                    )
                    t_grid3.cores.add(core)
                    t_grid3.save()

            core.is_indexed = True
            core.save()

