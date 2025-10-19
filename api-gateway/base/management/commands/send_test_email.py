from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, date, timedelta
import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from common.util.romsg import rp

from argparse import Namespace

import smtplib;
# 메일 메시지를 만드 모듈이다. (MIMEBase는 이하 MIMEMultipart, MIMEText, MIMEApplication, MIMEImage, MIMEAudio)의 상위 모듈이다.
# 굳이 선언할 필요없다.
#from email.mime.base import MIMEBase;
# 메일의 Data 영역의 메시지를 만드는 모듈 (MIMEText, MIMEApplication, MIMEImage, MIMEAudio가 attach되면 바운더리 형식으로 변환)
from email.mime.multipart import MIMEMultipart;
# 메일의 본문 내용을 만드는 모듈
from email.mime.text import MIMEText;
# 메일의 첨부 파일을 base64 형식으로 변환
from email.mime.application import MIMEApplication;
# 파일 IO
import io;
from email import utils
from email.header import Header

from common.util import datetime_util

# ./manage.py send_test_email --to="myounghoon.kim@gmail.com"

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            default='freehn@gmail.com'
        )

    def handle(self, *args, **options):

        sender_name, app_password = settings.GMAIL_APP_PASSWORD.split("|")
        sender_email = settings.GMAIL_SENDER

        data = MIMEMultipart();
        # 송신자 설정
        data['From'] = utils.formataddr((str(Header(sender_name, 'utf-8')), sender_email))

        # 메일 서버와 통신하기 전에 메시지를 만든다.
        # 수신자 설정 (복수는 콤마 구분이다.)
        data['To'] = options['to']
        print("To: " + data['To'])
        # 참조 수신자 설정
        # data['Cc'] = "nowonbun@gmail.com";
        # 숨은 참조 수신자 설정
        # data['Bcc'] = "nowonbun@gmail.com"
        # 메일 제목

        data['Subject'] = f"비트보트 비번입니다"
        print(data['Subject'])

        # 텍스트 형식의 본문 내용
        self.content = """
온 세상이 지옥같이 캄캄하게
나를 뒤덮은 밤의 어둠 속에서
나는 어떤 신들이든 그들에
내 불굴의 영혼 주심 감사하노라.

환경의 잔인한 손아귀에 잡혔을 때도
난 주춤거리지도 울지도 않았노라
운명의 몽둥이에 수없이 두들겨 맞아
내 머리 피 흘리지만 굴하지 않노라

분노와 눈물의 이승 저 너머엔
유령의 공포만이 섬뜩하게 떠오른다
허나 세월의 위협은 지금도 앞으로도
내 두려워하는 모습 보지 못하리라

상관치 않으리라, 천국 문 아무리 좁고
저승 명부 온갖 형벌 적혀있다 해도
나는 내 운명의 주인이요,
나는 내 영혼의 선장이나니
"""
        msg = MIMEText(self.content, 'plain');
        # Html 형식의 본문 내용 (cid로 이미 첨부 파일을 링크했다.)
        # msg = MIMEText("Hello Test<br /><img src='cid:capture'>", 'html')
        # Data 영역의 메시지에 바운더리 추가

        data.attach(msg);

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

        server.login(sender_email, app_password);
        # 심심하니 또 헤로 해주자.(의미 없음)
        server.ehlo();

        result = server.sendmail(data['From'], data['To'], data.as_string());
        print('----------------- result start ----------------------')
        print(result)
        print('----------------- result end ----------------------')
        server.quit();

