from django.conf import settings

import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

from common.util import juso_util, model_util, str_util

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone

import openpyxl

import geoinfo.models as geoinfo_models
import main.models as main_models
import main.serializers as main_serializers

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

class GeoUnitUpdater(object):

    def __init__(self, args={}):
        self.args = args

    def run(self):
        print('run GeoUnitUpdater', self.args)

        data = geoinfo_models.GeoUnit.objects.all()
        total_count = data.count()
        idx = 0
        for datum in data:
            idx =+ 1
            str_util.print_progress(idx, total_count, gap= 100, info='update geo info...')
            상가s = main_models.상가.objects.filter(geo_unit_id= datum.id)
            datum.상가_info = main_serializers.상가Serializer(상가s, many=True).data
            datum.info_updated_at = timezone.now()
            datum.save()
