from django.apps import apps
from django.contrib import admin
from django.utils.safestring import mark_safe

import core.models as core_models

from argparse import Namespace
class ArticleAdminBase(admin.ModelAdmin):
    ordering = ['-created_at',]
    search_fields = ['article_id', 'pnu']
    list_filter = ['updated_at', 'has_detail_text', 'is_detail_processed', 'is_detail_failed', '종류', '거래타입', 'sido',]
    list_display = [
        'article_id', '바로가기', 'created_at', 'updated_at', 'has_history',
        'detail_processed_at', 'has_detail_text', 'is_detail_processed', 'is_detail_failed',
        'title', '종류', '거래타입', '층', '한글층', '총층',
        'sido', 'sgg', 'emd', 'jb', 'pnu',
        '면적_평', '공급면적_평', '전용면적_평', '전용률',
        '매매가', '보증금', '임대료', '기보증금', '기월세',
        '공급면적_평당_매매가', '공급면적_평당_보증금', '공급면적_평당_임대료',
        '평당_매매가', '평당_보증금', '평당_임대료',
    ]

    def 바로가기(self, obj):
        return mark_safe(
            f'<a href="https://m.land.naver.com/article/info/{obj.article_id}" target="_blank">N</a>')


@admin.register(core_models.Article서울시)
class Article서울시Admin(ArticleAdminBase):
    pass

@admin.register(core_models.Article경기도)
class Article경기도Admin(ArticleAdminBase):
    pass
@admin.register(core_models.Article인천시)
class Article인천시Admin(ArticleAdminBase):
    pass

class ArticleHistoryAdminBase(admin.ModelAdmin):
    ordering = ['-created_at',]
    search_fields = ['article_id', 'pnu']
    list_filter = ['has_detail_text', 'is_detail_processed', 'is_detail_failed', '종류', '거래타입', 'sido',]
    list_display = [
        'article_id', '바로가기', 'gijun_date', 'detail_processed_at', 'has_detail_text', 'is_detail_processed', 'is_detail_failed',
        'title', '종류', '거래타입', '층', '한글층', '총층',
        'sido', 'sgg', 'emd', 'jb', 'pnu',
        '면적_평', '공급면적_평', '전용면적_평', '전용률',
        '매매가', '보증금', '임대료', '기보증금', '기월세',
        '공급면적_평당_매매가', '공급면적_평당_보증금', '공급면적_평당_임대료',
        '평당_매매가', '평당_보증금', '평당_임대료',
    ]

    def 바로가기(self, obj):
        return mark_safe(
            f'<a href="https://m.land.naver.com/article/info/{obj.article_id}" target="_blank">N</a>')

@admin.register(core_models.Article서울시History)
class Article서울시HistoryAdmin(ArticleHistoryAdminBase):
    pass

@admin.register(core_models.Article경기도History)
class Article경기도HistoryAdmin(ArticleHistoryAdminBase):
    pass

@admin.register(core_models.Article인천시History)
class Article인천시HistoryAdmin(ArticleHistoryAdminBase):
    pass

# @admin.register(core_models.ArticleHistory)
# class ArticleHistoryAdmin(admin.ModelAdmin):
#     ordering = ['-created_at',]
#     # list_filter = ['용도지역', '지목']
#     list_display = [field.name for field in core_models.ArticleHistory._meta.fields]
#     list_display = ['article_id', 'gijun_date'] + list_display
