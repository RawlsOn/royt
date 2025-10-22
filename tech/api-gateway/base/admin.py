from django.contrib import admin

import base.models as base_models

@admin.register(base_models.FrontendVersion)
class FrontendVersionAdmin(admin.ModelAdmin):
    # search_fields = ('key', )
    # list_filter = ('is_juso_updated',)
    list_display = ('note', 'created_at')