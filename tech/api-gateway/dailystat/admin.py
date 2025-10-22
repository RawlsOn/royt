from django.contrib import admin

from . import models

@admin.register(models.Emd)
class Admin(admin.ModelAdmin):
    ordering = ['-created_at',]
    list_filter = ['gijun_date', 'gijun_date_str', 'sido', 'sgg', 'emd']
    list_display = [field.name for field in models.Emd._meta.fields]
