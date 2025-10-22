from django.contrib import admin
from django.utils.safestring import mark_safe

from rticler.models.board import Board
from rticler.models.article import Article
from rticler.models.article import TempArticle

@admin.register(Board)
class BoardInfoAdmin(admin.ModelAdmin):
    search_fields = [field.name for field in Board._meta.fields]
    list_display = [field.name for field in Board._meta.fields]

@admin.register(Article)
class ArticleInfoAdmin(admin.ModelAdmin):
    search_fields = [field.name for field in Article._meta.fields]
    list_display = [field.name for field in Article._meta.fields]

@admin.register(TempArticle)
class TempArticleInfoAdmin(admin.ModelAdmin):
    search_fields = [field.name for field in TempArticle._meta.fields]
    list_display = [field.name for field in TempArticle._meta.fields]
