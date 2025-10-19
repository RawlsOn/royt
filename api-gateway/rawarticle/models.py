from django.db import models
import base.models as base_models
from datetime import datetime, date, timedelta

# ./manage.py makemigrations rawarticle
# ./manage.py migrate rawarticle --database=rawarticle

# 어차피 람다로 넣을 거라 마이그레이션 필요 없음 쌩쿼리로
# 글고 11개시도로 나눌 것
# 즉 ProtoArticle서울시, ProtoArticle인천시 이런 식으로

class ProtoArticle(base_models.RoBase):
    article_id = models.CharField(max_length= 16, db_index= True)
    lgeo = models.CharField(max_length= 16, blank=True, null=True)
    cortarNo = models.CharField(max_length= 16, blank=True, null=True)

    sido = models.CharField(max_length= 16, blank=True, null=True)
    sgg = models.CharField(max_length= 16, blank=True, null=True)
    emd = models.CharField(max_length= 16, blank=True, null=True)

    list_text = models.TextField()
    is_processed = models.BooleanField(default= False, db_index=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['article_id', 'created_date'],
                name='unique_article'
            )
        ]

class Region(base_models.RoBase):
    title = models.CharField(max_length= 16)
    code = models.CharField(max_length= 16)
    cortarType = models.CharField(max_length= 16)
    regionType = models.CharField(max_length= 8, db_index= True)
    x = models.CharField(max_length= 16)
    y = models.CharField(max_length= 16)

    sido = models.CharField(max_length= 16, blank=True, null=True)
    sgg = models.CharField(max_length= 16, blank=True, null=True)
    emd = models.CharField(max_length= 16, blank=True, null=True)

    is_updated = models.BooleanField(default= False)
    update_start_time = models.DateTimeField(blank= True, null=True)
    update_end_time = models.DateTimeField(blank= True, null=True)

    def __str__(self):
        return self.title + ' ' + self.code

class Cluster(base_models.RoBase):
    lgeo = models.CharField(max_length= 16, db_index= True)
    lat = models.CharField(max_length= 16)
    lon = models.CharField(max_length= 16)
    psr = models.CharField(max_length= 16)
    z = models.PositiveSmallIntegerField()
    count = models.PositiveSmallIntegerField()
    done_url = models.TextField(blank=True, null=True)
    final_url = models.TextField(blank=True, null=True)

    sido = models.CharField(max_length= 16, blank=True, null=True)
    sgg = models.CharField(max_length= 16, blank=True, null=True)
    emd = models.CharField(max_length= 16)
    parent = models.CharField(max_length= 16)

    is_collecting = models.BooleanField(default= False)
    article_collection_start_time = models.DateTimeField(
        default= datetime.strptime('1970-01-01', '%Y-%m-%d')
    )
    article_collection_end_time = models.DateTimeField(
        default= datetime.strptime('1970-01-01', '%Y-%m-%d')
    )
    article_collected_date = models.DateField(
        default= datetime.strptime('1970-01-01', '%Y-%m-%d'),
        db_index= True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['lgeo', 'parent'],
                name='unique_cluster'
            )
        ]

class RegionInstanceMap(base_models.RoBase):
    region = models.CharField(max_length= 32, db_index= True)
    aws_region = models.CharField(max_length= 32, db_index= True)
    instance_id = models.CharField(max_length= 32, db_index= True)
    state = models.CharField(max_length= 16, db_index= True)
    launch_time = models.DateTimeField()

class BlockedIp(base_models.RoBase):
    instance_id = models.CharField(max_length= 32, db_index= True)
    ip = models.CharField(max_length= 32, db_index= True)
    launch_time_when_blocked = models.DateTimeField(null=True, blank=True)
    aws_region = models.CharField(max_length= 16, db_index= True, blank=True, null=True)

class InstanceMonitoring(base_models.RoBase):
    running = models.PositiveSmallIntegerField(default= 0)
    stopped = models.PositiveSmallIntegerField(default= 0)
    pending = models.PositiveSmallIntegerField(default= 0)
    shutting_down = models.PositiveSmallIntegerField(default= 0)
    stopping = models.PositiveSmallIntegerField(default= 0)
    terminated = models.PositiveSmallIntegerField(default= 0)

class ArticleCollectorTargetCount(base_models.RoBase):
    us_east_1 = models.PositiveSmallIntegerField(default= 0)
    us_east_2 = models.PositiveSmallIntegerField(default= 0)
    us_west_1 = models.PositiveSmallIntegerField(default= 0)
    us_west_2 = models.PositiveSmallIntegerField(default= 0)
    af_south_1 = models.PositiveSmallIntegerField(default= 0)
    ap_east_1 = models.PositiveSmallIntegerField(default= 0)
    ap_south_2 = models.PositiveSmallIntegerField(default= 0)
    ap_southeast_3 = models.PositiveSmallIntegerField(default= 0)
    ap_southeast_4 = models.PositiveSmallIntegerField(default= 0)
    ap_south_1 = models.PositiveSmallIntegerField(default= 0)
    ap_northeast_3 = models.PositiveSmallIntegerField(default= 0)
    ap_southeast_1 = models.PositiveSmallIntegerField(default= 0)
    ap_southeast_2 = models.PositiveSmallIntegerField(default= 0)
    ap_northeast_1 = models.PositiveSmallIntegerField(default= 0)
    ca_central_1 = models.PositiveSmallIntegerField(default= 0)
    eu_central_1 = models.PositiveSmallIntegerField(default= 0)
    eu_west_1 = models.PositiveSmallIntegerField(default= 0)
    eu_west_2 = models.PositiveSmallIntegerField(default= 0)
    eu_south_1 = models.PositiveSmallIntegerField(default= 0)
    eu_west_3 = models.PositiveSmallIntegerField(default= 0)
    eu_south_2 = models.PositiveSmallIntegerField(default= 0)
    eu_north_1 = models.PositiveSmallIntegerField(default= 0)
    eu_central_2 = models.PositiveSmallIntegerField(default= 0)
    il_central_1 = models.PositiveSmallIntegerField(default= 0)
    me_south_1 = models.PositiveSmallIntegerField(default= 0)
    me_central_1 = models.PositiveSmallIntegerField(default= 0)
    sa_east_1 = models.PositiveSmallIntegerField(default= 0)

class ArticleDetailCollectorControl(base_models.RoBase):
    percent = models.PositiveSmallIntegerField(default= 10)

class BaseImage(base_models.RoBase):
    region = models.CharField(max_length= 32)
    region_alias = models.CharField(max_length= 32)
    image_name = models.CharField(max_length= 32)
    security_group = models.CharField(max_length= 32)
    instance_type = models.CharField(max_length= 32)
    key_name = models.CharField(max_length= 32)