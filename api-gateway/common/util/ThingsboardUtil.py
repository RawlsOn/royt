from django.conf import settings
from common.util.romsg import rp

import io, time, os, glob, pprint, json, re, shutil, ntpath, sys
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from datetime import datetime, date, timedelta
# from django.utils import timezone
from pytz import timezone
import requests

class ThingsboardUtil(object):

    def __init__(self, args={}):
        self.args = args
        self.device_token = self.args.device_token
        self.base_url = self.args.base_url

    def send(self, telemetry):
        pp.pprint(telemetry)
        url = self.base_url + '/api/v1/' + self.device_token + '/telemetry'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.post(url, headers=headers, json=telemetry)
        print(response.status_code)
        print(response.text)