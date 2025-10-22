from django.contrib import admin

import monitoring.models as m_models

@admin.register(m_models.Article)
class ArticleAdmin(admin.ModelAdmin):
    ordering = ['-created_at',]
    list_display = [
        'created_at',
        '서울시_total',
        '서울시_has_detail',
        # '서울시_has_detail_gap',
        # '서울시_is_detail_processed',
        # '서울시_is_detail_failed',
        '서울시_is_pnu_null',

        '경기도_total',
        '경기도_has_detail',
        # '경기도_has_detail_gap',
        # '경기도_is_detail_processed',
        # '경기도_is_detail_failed',
        '경기도_is_pnu_null',
        '인천시_total',

        '인천시_has_detail',
        # '인천시_has_detail_gap',
        # '인천시_is_detail_processed',
        # '인천시_is_detail_failed',
        '인천시_is_pnu_null',
    ]

@admin.register(m_models.ArticleProto)
class ArticleProtoAdmin(admin.ModelAdmin):
    ordering = ['-created_at',]
    list_display = [field.name for field in m_models.ArticleProto._meta.fields]

# Register your models here.
