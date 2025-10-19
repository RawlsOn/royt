from django.conf import settings
from common.util.romsg import rp

from common.util import juso_util, model_util, str_util
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv, random
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

from common.util import datetime_util, dict_util
from django.contrib.gis.geos import Point
from django.apps import apps
from argparse import Namespace

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone

pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from common.util.RoPrinter import RoPrinter
PRINT_GAP = 10

from roemail.workers.RoMailer import RoMailer
import roemail.models as roemail_models

# ./manage.py run_worker --baseapp=roemail --worker=SendLoginjoinCodeRoMailer

class SendLoginjoinCodeRoMailer(RoMailer):

    def __init__(self, args={}):
        super().__init__(args)
        printer = RoPrinter(f'SendLoginjoinCodeRoMailer')
        self.rp = printer.rp
        self.ps = str_util.ProgressShower(gap=PRINT_GAP, info=f'SendLoginjoinCodeRoMailer')
        self.ps.printer = printer
        self.args = args
        self.mail = Namespace()

        self.mail.receiver = self.args.get('email', None)
        if not self.mail.receiver:
            self.mail.receiver = 'freehn@gmail.com'

    def run(self):
        print(f'run SendLoginjoinCodeRoMailer')

        self.make_code()
        self.send(send_type='sync')

        pp.pprint(self.mail)

    def make_code(self):
        code = f'{random.randrange(1, 10**6):06}'
        code = code[:3] + ' ' + code[3:]
        self.to_create = dict(
            email=self.mail.receiver,
            code= code
        )
        roemail_models.EmailLoginjoinCode.objects.create(**self.to_create)

        self.mail.subject = f'로그인 코드: {self.to_create["code"]}'
        self.mail.content_type = 'plain'
        self.mail.content = f"""로그인 코드: {self.to_create["code"]}"""



        # roemail_models.EmailLoginjoinCode.objects.filter(
        #     email= self.mail.receiver,
        #     loginjoin_at__isnull=True,
        #     created_at__lt=datetime_util.now() - timedelta(minutes=5)
        # )



