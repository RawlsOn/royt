from django.conf import settings
from common.util.romsg import rp

from common.util import juso_util, model_util, str_util
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv, random
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

from common.util import datetime_util, dict_util
from django.contrib.gis.geos import Point
from django.apps import apps

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone

pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from common.util.RoPrinter import RoPrinter
PRINT_GAP = 10

class RoMailPreparer(object):

    def __init__(self, args={}):
        printer = RoPrinter(f'RoMailPreparer')
        self.rp = printer.rp
        self.ps = str_util.ProgressShower(gap=PRINT_GAP, info=f'RoMailPreparer')
        self.ps.printer = printer
        self.args = args

    def run(self):
        print(f'run RoMailPreparer')
