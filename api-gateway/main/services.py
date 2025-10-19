from django.conf import settings
from dotenv import load_dotenv
load_dotenv(verbose=True)

import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from common.util import str_util
from common.util.logger import RoLogger
from common.util.ProgressWatcher import ProgressWatcher
logger = RoLogger(another_output_file= settings.LOG_FILE)

from django.utils import timezone
import requests, urllib



import main.models as main_models

class FrontendVersionService:
    @staticmethod
    def get(params):
        # data = main_models.FrontendVersion.objects.filter(
        #     kb_danji_id= params['danji_id'],
        #     kb_area_id= params['area_id']
        # )
        return main_models.FrontendVersion.objects.first()

