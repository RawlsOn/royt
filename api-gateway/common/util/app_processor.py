from django.conf import settings
from django.apps import apps
import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from common.util.str_util import camel_to_dash

class AppProcessor(object):

    def __init__(self, args):
        self.args = args
        self.models = apps.all_models[args.app_name]
        self.model_instances = []
        for model in self.models:
            self.model_instances.append(apps.get_model(args.app_name, model))

    def run(self):
        print('AppProcessor')

        self.write_serializer_str()
        self.write_admin_str()
        self.write_api_str()
        self.write_url_str()

        for instance in self.model_instances:
            self.write_serializers(instance)
            self.write_admin(instance)
            self.write_apis(instance)
            self.write_urls(instance)

        self.write_url_str_ending()

    def write_serializer_str(self):
        target_str = f"""
from rest_framework import serializers

from {self.args.app_name}.models import *
"""
        target_file = settings.BASE_DIR / self.args.app_name / 'serializers.py'
        with open(target_file, 'w') as f:
            f.write(target_str)

    def write_serializers(self, instance):
        app_name = self.args.app_name
        model_name = instance._meta.model.__name__
        # print([f.name for f in instance._meta.get_fields()])

        target_str = f"""

class {model_name}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {model_name}
        fields = '__all__'"""

        target_file = settings.BASE_DIR / app_name / 'serializers.py'
        with open(target_file, 'a') as f:
            f.write(target_str)

    def write_admin_str(self):
        app_name = self.args.app_name
        target_str = f"""
from django.contrib import admin

from {app_name}.models import *
"""
        target_file = settings.BASE_DIR / app_name / 'admin.py'
        with open(target_file, 'w') as f:
            f.write(target_str)

    def write_admin(self, instance):
        app_name = self.args.app_name
        model_name = instance._meta.model.__name__

        target_str = f"""

@admin.register({model_name})
class {model_name}Admin(admin.ModelAdmin):
    ordering = ('-created_at', )
    search = [field.name for field in {model_name}._meta.fields]
    list_display = [field.name for field in {model_name}._meta.fields]"""

        target_file = settings.BASE_DIR / app_name / 'admin.py'
        with open(target_file, 'a') as f:
            f.write(target_str)

    def write_api_str(self):
        app_name = self.args.app_name
        target_str = f"""

from rest_framework import generics

from rest_framework.permissions import AllowAny

from {app_name}.models import *
from {app_name}.serializers import *
"""
        target_file = settings.BASE_DIR / app_name / 'apis.py'
        with open(target_file, 'w') as f:
            f.write(target_str)

    def write_apis(self, instance):
        app_name = self.args.app_name
        model_name = instance._meta.model.__name__

        target_str = f"""

class {model_name}(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = {model_name}Serializer
    allowed_methods = ('GET',)
    queryset = {model_name}.objects.all()"""

        target_file = settings.BASE_DIR / app_name / 'apis.py'
        with open(target_file, 'a') as f:
            f.write(target_str)

    def write_url_str(self):
        app_name = self.args.app_name
        target_str = f"""

from django.urls import re_path, path, include

from {app_name} import apis
urlpatterns = [
"""
        target_file = settings.BASE_DIR / app_name / 'urls.py'
        with open(target_file, 'w') as f:
            f.write(target_str)

    def write_urls(self, instance):
        app_name = self.args.app_name
        model_name = instance._meta.model.__name__
        print(model_name)
        target_str = f"""
    path(
        '{camel_to_dash(model_name)}',
        apis.{model_name}.as_view(),
        name="api_{model_name}"
    ),
"""
        target_file = settings.BASE_DIR / app_name / 'urls.py'
        with open(target_file, 'a') as f:
            f.write(target_str)

    def write_url_str_ending(self):
        target_str = f"""
]
"""
        target_file = settings.BASE_DIR / self.args.app_name / 'urls.py'
        with open(target_file, 'a') as f:
            f.write(target_str)
