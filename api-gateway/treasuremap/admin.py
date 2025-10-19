from django.apps import apps
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.files import File
from django.urls import path, re_path, include
from django.http import HttpResponseRedirect,HttpResponse
import uuid

import robasev2.models as tm_models

from argparse import Namespace
from robasev2.workers.ExcelLoader import ExcelLoader

@admin.register(tm_models.Note)
class NoteAdmin(admin.ModelAdmin):
    change_list_template = "admin/toji_change_list.html"
    ordering = ['-created_at',]
    list_display = [field.name for field in tm_models.Note._meta.fields]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('loadexcel/', self.set_loadexcel),
        ]
        return my_urls + urls

    def set_loadexcel(self, request):
        print('set_loadexcel~~~~~~~~~~~~~~~~~', request.FILES['fileToUpload'])
        file = request.FILES['fileToUpload']
        path_to_write = '/usr/data/' + settings.PROJECT_NAME + '/upload/' + str(uuid.uuid4()) + '.xlsx'
        with open(path_to_write, 'wb') as f:
            f.write(file.read())

        print('file', path_to_write)
        # loader = ExcelLoader(Namespace(**{'file_path': path_to_write}))
        # loader.run()
        self.message_user(request, "데이터 적재 완료")
        return HttpResponseRedirect("../")
