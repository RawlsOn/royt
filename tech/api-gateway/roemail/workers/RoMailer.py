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
import roemail.models as roemail_models

import smtplib;
from email.mime.multipart import MIMEMultipart;
from email.mime.text import MIMEText;
from email.mime.application import MIMEApplication;
from email import utils
from email.header import Header

class RoMailer(object):

    def __init__(self, args={}):
        printer = RoPrinter(f'RoMailer')
        self.rp = printer.rp
        self.ps = str_util.ProgressShower(gap=PRINT_GAP, info=f'RoMailer')
        self.ps.printer = printer
        self.args = args

    def run(self):
        print(f'run RoMailer')
        print(self.args)
        preparer = getattr(self.args, 'preparer', None)
        if not preparer:
            from roemail.workers.SendLoginjoinCodeRoMailPreparer import SendLoginjoinCodeRoMailPreparer
            preparer = SendLoginjoinCodeRoMailPreparer(self.args)

        print(preparer)

    def send(self, send_type='async'):
        data = MIMEMultipart();
        sender_name, app_password = settings.GMAIL_APP_PASSWORD.split("|")
        sender_email = settings.GMAIL_SENDER
        data['From'] = utils.formataddr((str(Header(sender_name, 'utf-8')), sender_email))
        data['To'] = self.mail.receiver
        data['Subject'] = self.mail.subject
        msg = MIMEText(self.mail.content, self.mail.content_type)
        data.attach(msg)

        # 메일 서버와 telnet 통신 개시
        # server = smtplib.SMTP_SSL('smtp.gmail.com',465);
        server = smtplib.SMTP('smtp.gmail.com',587);
        # 메일 통신시 디버그
        server.set_debuglevel(1);
        # 헤로 한번 해주자.(의미 없음)
        # server.ehlo();
        # tls 설정 주문 - tls 587 포트의 경우
        server.starttls();
        # 헤로 또 해주자.(의미 없음)
        # server.ehlo();
        # 로그인 한다.

        try:
            server.login(sender_email, app_password);
            # 심심하니 또 헤로 해주자.(의미 없음)
            server.ehlo();

            result = server.sendmail(data['From'], data['To'], data.as_string());
            server.quit();
        except Exception as e:
            result = dict(error=str(e))
            server.quit();

        send_job = roemail_models.SendJob.objects.create(
            to=self.mail.receiver,
            subject=self.mail.subject,
            content_type=self.mail.content_type,
            content=self.mail.content,
            send_type=send_type
        )
        del self.mail.content
        self.mail.result = result
        roemail_models.SendLog.objects.create(
            job_id=send_job.id,
            tag='send',
            is_success=result == {},
            text= json.dumps(vars(self.mail), ensure_ascii=False, indent=2)
        )
