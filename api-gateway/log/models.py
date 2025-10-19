from django.conf import settings
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db import models
import base.models as base_models
from django.contrib.gis.db import models as gis_models
from django.apps import apps

import uuid
from django.db.models.signals import post_save

import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv, random
from common.util import juso_util, model_util, str_util, geo_util

pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from common.util.RoPrinter import RoPrinter
PRINT_GAP = 100
printer = RoPrinter('ydjycore model')
rp = printer.rp
ps = str_util.ProgressShower(gap=PRINT_GAP, info='ydjycore model')
ps.printer = printer

# rm /usr/data/rostateplanlocal/ydjycore_db.sqlite3;
# rm ydjycore/migrations/00*
# ./manage.py makemigrations ydjycore
# ./manage.py migrate ydjycore --database=ydjycore

from django.db import models

# very large bbox
# http://localhost:4117/api/auctioncore/core/?in_bbox=126.5,36.051841,127.5,37.0


class CoreQuerySet(models.QuerySet):
    def indexed_bbox_filter(self, bbox):
        rp('indexed_bbox_filter')

        Grid2 = apps.get_model('grid12', 'Grid2')

        grid2_ids = list(Grid2.objects.filter(geom__intersects=bbox).values_list('id', flat=True))
        rp(f'bbox grid2s count {len(grid2_ids)}')
        rp(f'all CoreGrid3 count {Grid3.objects.count()}')
        core_grid3s = Grid3.objects.filter(
            grid2_id__in=grid2_ids,
        ).filter(
            geom__intersects=bbox,
        )
        rp(f'filtered CoreGrid3 count {core_grid3s.count()}')
        # for core_grid3 in core_grid3s:
            # pp.pprint(core_grid3.__dict__)

        cores = self.filter(
            grid3__in=core_grid3s,
            geom__intersects=bbox,
        ).distinct() # 디스팅트 써도 괜찮은 건지 모르겠음
        # __in 필터 때문에 같은 게 두 개 나올 떄가 있음

        rp(f'cores count {cores.count()}')

        return cores

class CoreAbstract(base_models.RoBase):
    objects = CoreQuerySet.as_manager()

    gijun_date = models.DateField(null=True, blank=True, db_index=True)
    gijun_date_str = models.CharField(max_length=10, null=True, blank=True, db_index=True)

    geom = gis_models.MultiPolygonField(srid=4326, blank=True, null=True)
    center = gis_models.PointField(srid=4326, blank=True, null=True)

    # sido, sgg는 어차피 필요없음. 지적도가 아닌 이상 두 개 이상에 속할 수가 있기 때문.

    원천도형ID = models.IntegerField(null=True, blank=True)
    도면번호 = models.CharField(max_length=33, null=True, blank=True)
    주제도면 = models.CharField(max_length=254, null=True, blank=True)
    데이터기준일자 = models.DateField(null=True, blank=True)
    원천시도시군구코드 = models.CharField(max_length=5, null=True, blank=True)

    code = models.CharField(max_length=8, null=True, blank=True, db_index=True)
    yongdo = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    yongdo_detail = models.CharField(max_length=64, null=True, blank=True, db_index=True)

    is_indexed = models.BooleanField(default=False, db_index=True)

    is_removed = models.BooleanField(default=False, db_index=True)
    removed_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    @property
    def title(self):
        return f'{self.yongdo} {self.yongdo_detail} {self.원천시도시군구코드}'

    @property
    def all_prop(self):
        ret = self.__dict__
        del ret['geom']
        ret['history'] = [x.all_prop for x in self.history_set.all()]
        return ret

    def update(self, new_entry):
        for k, v in new_entry.items():
            setattr(self, k, v)

        self.save()

class Core(CoreAbstract):
    id = models.CharField(max_length=64, primary_key=True)

class CoreHistory(CoreAbstract):
    core = models.ForeignKey(Core, on_delete=models.CASCADE, related_name='history_set')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['core', 'gijun_date_str'],
                name='ydjycore_unique_core_gijun_date_str'
            )
        ]

class Grid3(base_models.RoBase):
    geom = gis_models.MultiPolygonField(srid=4326)
    grid2_id = models.IntegerField(null=True, blank=True, db_index=True)
    cores = models.ManyToManyField(Core, blank=True, db_index=True)