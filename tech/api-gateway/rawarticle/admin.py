from django.contrib import admin

import rawarticle.models as rawarticle_models

@admin.register(rawarticle_models.ProtoArticle)
class ProtoArticleAdmin(admin.ModelAdmin):
    ordering = ['-created_at',]
    search_fields = ['article_id', 'lgeo']
    list_filter = ['created_date', 'sido', 'sgg',]
    list_display = ['article_id', 'lgeo', 'cortarNo', 'sido', 'sgg', 'emd', 'created_date', 'created_at', 'is_processed', 'processed_at', ]

@admin.register(rawarticle_models.Region)
class RegionAdmin(admin.ModelAdmin):
    ordering = ['code',]
    list_filter = ['updated_at', 'regionType', 'sido', 'sgg']
    list_display = [
        'title', 'updated_at', 'code', 'cortarType', 'regionType', 'sido', 'sgg', 'emd', 'update_start_time', 'update_end_time'
    ]

@admin.register(rawarticle_models.Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_filter = ['article_collected_date', 'is_collecting', 'sido']
    search_fields = ['lgeo', 'sido', 'sgg', 'emd', 'parent']
    list_display = [
        'id', 'lgeo', 'lat', 'lon', 'count', 'sido', 'sgg', 'emd', 'parent', 'is_collecting', 'created_at', 'updated_at', 'article_collected_date', 'article_collection_start_time', 'article_collection_end_time'
    ]
@admin.register(rawarticle_models.RegionInstanceMap)
class RegionInstanceMapAdmin(admin.ModelAdmin):
    list_filter = ['region', 'aws_region', 'state']
    list_display = [field.name for field in rawarticle_models.RegionInstanceMap._meta.fields]

@admin.register(rawarticle_models.BlockedIp)
class BlockedIpAdmin(admin.ModelAdmin):
    list_filter = ['created_date']
    search_fields = ['instance_id', 'ip']
    list_display = [field.name for field in rawarticle_models.BlockedIp._meta.fields]

@admin.register(rawarticle_models.InstanceMonitoring)
class InstanceMonitoringAdmin(admin.ModelAdmin):
    list_display = [field.name for field in rawarticle_models.InstanceMonitoring._meta.fields]

@admin.register(rawarticle_models.ArticleCollectorTargetCount)
class ArticleCollectorTargetCountAdmin(admin.ModelAdmin):
    list_display = [field.name for field in rawarticle_models.ArticleCollectorTargetCount._meta.fields]

@admin.register(rawarticle_models.ArticleDetailCollectorControl)
class ArticleDetailCollectorControlAdmin(admin.ModelAdmin):
    list_display = [field.name for field in rawarticle_models.ArticleDetailCollectorControl._meta.fields]
@admin.register(rawarticle_models.BaseImage)
class BaseImageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in rawarticle_models.BaseImage._meta.fields]