from django.apps import apps
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.files import File
from django.urls import path, re_path, include
from django.http import HttpResponseRedirect,HttpResponse
import uuid

import geoinfo.models as geoinfo_models

@admin.register(geoinfo_models.GeoUnit)
class GeoUnitAdmin(admin.ModelAdmin):
    change_list_template = "admin/toji_change_list.html"
    ordering = ['-created_at',]
    search_fields = ['주소_input', '지번주소', '도로명주소', 'pnu']
    # list_filter = ['시도', 'geo_type', '시군구']
    list_display = [field.name for field in geoinfo_models.GeoUnit._meta.fields]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('loadexcel/', self.set_loadexcel),
        ]
        return my_urls + urls

    def set_loadexcel(self, request):
        print('set_loadexcel~~~~~~~~~~~~~~~~~', request.FILES['fileToUpload'])
        file = request.FILES['fileToUpload']
        path_to_write = f'/usr/data/{settings.PROJECT_NAME}-{settings.RUNNING_ENV}/upload/' + str(uuid.uuid4()) + '.xlsx'
        with open(path_to_write, 'wb') as f:
            f.write(file.read())

        print('file', path_to_write)
        # loader = ExcelLoader(Namespace(**{'file_path': path_to_write}))
        # loader.run()
        self.message_user(request, "데이터 적재 완료")
        return HttpResponseRedirect("../")
