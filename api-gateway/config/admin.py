
from django.contrib import admin

from config.models import *

# from import_export.admin import ImportExportModelAdmin

import config.models as config_models

@admin.register(config_models.SEO)
class SEOAdmin(admin.ModelAdmin):
    ordering = ['-created_at',]
    search_fields = ['content',]
    list_display = [field.name for field in config_models.SEO._meta.fields]

@admin.register(config_models.BaseSetting)
class SettingAdmin(admin.ModelAdmin):
    ordering = ['-created_at',]
    search_fields = ['content',]
    list_display = [field.name for field in config_models.BaseSetting._meta.fields]
