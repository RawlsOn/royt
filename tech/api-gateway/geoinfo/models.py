from itertools import chain

from django.contrib.gis.db import models
import base.models as base_models

from django.conf import settings

# ./manage.py makemigrations geoinfo
# ./manage.py migrate geoinfo --database=geoinfo

def to_dict(instance):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields):
        if f.name == 'point' or f.name == 'center':
            data[f.name] = str(f.value_from_object(instance).x) + ',' + str(f.value_from_object(instance).y)
            continue
        data[f.name] = f.value_from_object(instance)
    # for f in opts.many_to_many:
    #     data[f.name] = [i.id for i in f.value_from_object(instance)]
    return data

class GisBase(models.Model):

    created_date = models.DateField(auto_now_add=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    multipoly = models.MultiPolygonField(blank=True, null=True)
    point = models.PointField(blank=True, null=True)
    center = models.PointField(blank=True, null=True)

    class Meta:
        abstract= True
        # first로 얻을 때 가장 오래된 것이 나옴
        ordering = ('created_at', )

    @property
    def to_obj(self):
        dict_obj = to_dict(self)
        return dict_obj

    @property
    def center_x(self):
        if self.center:
            return self.center.x
        return None

    @property
    def center_y(self):
        if self.center:
            return self.center.y
        return None

class GeoUnit(GisBase):

    class GeoTypeChoices(models.TextChoices):
        PNU = 'PNU'
        MULTI_PNU = 'MULTI_PNU'
        SECTOR = 'SECTOR'
        OTHERS = 'OTHERS'
    geo_type = models.CharField(
        max_length=16, choices=GeoTypeChoices.choices, default='PNU')

    주소_input = models.CharField(max_length= 255, blank=True, null=True, db_index=True) # 입력값으로 사용하는 값

    uniq_title = models.CharField(max_length= 255, blank=True, null=True, db_index=True) # 지번주소 / 타이틀인 이유는 개발계획 같은 것도 title이 될 수 있으므로

    지번주소 = models.CharField(max_length= 255, blank=True, null=True)
    # 도로명주소 불러올 때 point, center 저장
    도로명주소 = models.CharField(max_length= 255, blank=True, null=True)

    pnu = models.CharField(max_length=32, blank=True, null=True)

    시도 = models.CharField(max_length=32, blank=True, null=True)
    시군구 = models.CharField(max_length=32, blank=True, null=True)
    읍면동 = models.CharField(max_length=32, blank=True, null=True)
    산 = models.BooleanField(blank=True, null=True)

    본번 = models.CharField(max_length=4, blank=True, null=True)
    부번 = models.CharField(max_length=4, blank=True, null=True)
    지하 = models.BooleanField(blank=True, null=True)
    zone_no = models.CharField(max_length=8, blank=True, null=True)

    info = models.TextField(blank=True, null=True)
    info_updated_at = models.DateTimeField(db_index=True, blank=True, null=True)

    step1_gis_업데이트 = models.BooleanField(default= False)
    step1_gis_업데이트_at = models.DateTimeField(blank=True, null=True)

    토지_count = models.PositiveSmallIntegerField(default= 0)
    건물_count = models.PositiveSmallIntegerField(default= 0)
    상가_count = models.PositiveSmallIntegerField(default= 0)
    total_물건_count = models.PositiveSmallIntegerField(default= 0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['주소_input', 'uniq_title'],
                name='unique_geounit'
            )
        ]

    def __str__(self):
        if self.주소_input:
            return self.주소_input
        return ''