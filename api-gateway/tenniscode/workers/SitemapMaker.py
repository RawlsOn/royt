from django.conf import settings


import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models import QuerySet

import common.util.datetime_util as datetime_util
import common.util.str_util as str_util
from common.util.logger import RoLogger
logger = RoLogger()
import urllib.parse

from dateutil.relativedelta import relativedelta
import tenniscode.models as tenniscode_models
import history.models as history_models

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# ./manage.py run_sitemap_maker

class SitemapMaker(object):
    def __init__(self, args={}):
        self.args = args

    def run(self):
        print('run SitemapMaker')
        result_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
        lastmod_date = timezone.now().strftime('%Y-%m-%d')
        for club in tenniscode_models.Club.objects.all():
            title = urllib.parse.quote_plus(club.title)
            loc = f"{self.args.base_url}/club/{title}/"
            result_content += f'''
<url>
    <loc>{loc}</loc>
    <lastmod>{lastmod_date}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
</url>
'''
        result_content += '</urlset>'

        filename = self.args.target_folder + '/sitemap.xml'
        print('write to ' + filename)
        with open(filename, 'w') as f:
            f.write(result_content)

        # with gzip.open(result_file, 'wt') as f:
        #     f.write(result_content)

