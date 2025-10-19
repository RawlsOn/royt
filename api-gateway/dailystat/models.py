from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db import models
import base.models as base_models
import common.util.model_util as model_util
import uuid

import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# ./manage.py makemigrations dailystat
# ./manage.py migrate dailystat --database=dailystat

class Emd(base_models.RoBase):
    fullname = models.CharField(max_length= 64, db_index=True)
    sido = models.CharField(max_length= 16, db_index=True)
    sgg = models.CharField(max_length= 16, db_index=True)
    emd = models.CharField(max_length= 16, db_index=True)

    gijun_date = models.DateField(blank=True, null=True, db_index=True)
    gijun_date_str = models.CharField(max_length= 16, blank=True, null=True, db_index=True)
    proto_created_count = models.PositiveIntegerField(default=0)
    created_count = models.PositiveIntegerField(default=0)
    updated_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('fullname', 'gijun_date_str')