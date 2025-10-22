# 2024-02-17
# cp /Users/kimmyounghoon/Works/mkay/common/api-gateway/main/management/commands/* ./api-gateway/main/management/commands/


from django.core.management.base import BaseCommand, CommandError
from argparse import Namespace

import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

import io, time, os, glob
import boto3, zipfile

from django.contrib.gis.gdal import DataSource, SpatialReference, CoordTransform
from django.contrib.gis.geos import MultiPolygon, Polygon, fromstr

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--target',
            required= True
        )
        parser.add_argument(
            '--encoding',
            default= 'utf-8'
        )

    def handle(self, *args, **options):
        self.options = options
        self.run()

    def run(self):
        print(self.options)

        ds = DataSource(self.options['target'])
        lyr = ds[0]
        ds.encoding = self.options['encoding']
        print('fields', [fld for fld in lyr.fields])

        print(len(lyr))
        mod = int(len(lyr) / 10)
        for idx, feat in enumerate(lyr):
            if idx % mod != 0: continue
            print(idx, '------------------------')
            to_print = {}
            for fld in lyr.fields:
                # to_print.append(feat.get(fld))
                to_print[fld] = feat.get(fld)
            pp.pprint(to_print)
