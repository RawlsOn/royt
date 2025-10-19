from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db import models
import base.models as base_models
import uuid
from django.db.models.signals import post_save

import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# import geoinfo.models as geoinfo_models
import user.models as user_models

# ./manage.py makemigrations main
# ./manage.py migrate main