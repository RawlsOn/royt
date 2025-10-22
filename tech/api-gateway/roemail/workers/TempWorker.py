from django.conf import settings
from common.util.romsg import rp

from common.util import juso_util, model_util, str_util
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv, random
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
ps = str_util.ProgressShower(gap=10, info='JijeokLoader')

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

import common.util.datetime_util as dt_util
from django.contrib.gis.geos import Point
from django.apps import apps

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone

from django.contrib.gis.gdal import DataSource, SpatialReference, CoordTransform
from django.contrib.gis.geos import MultiPolygon, Polygon, fromstr
from common.custom.CustomLayerMapping import CustomLayerMapping
import core.models as core_models

# ./manage.py run_jijeok_loader

class JijeokLoader(object):

    def __init__(self, args={}):
        self.args = args

    def run(self):
        print('run JijeokLoader')

        # epsg5174 = '+proj=tmerc +lat_0=38 +lon_0=127.0028902777778 +k=1 +x_0=200000 +y_0=500000 +ellps=bessel +units=m +no_defs +towgs84=-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43'

        self.load()
