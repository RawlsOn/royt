import os
import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.conf import settings
from common.util.slack import fire
import json, copy

class RoLogger(object):

    def __init__(self, another_output_file='', verbose=True, title=''):
        self.another_output_file = another_output_file
        self.verbose = verbose
        self.title = title

    def write(self, log_type, log_title, log_json=None):
        log_obj = {}
        if log_json is not None:
            log_obj = json.loads(log_json)

        log_obj['_META_RUNNING_ENV'] = os.getenv('RUNNING_ENV')
        log_obj['_META_SERVICE_ID'] = os.getenv('SERVICE_ID')
        log_obj['_META_DATETIME'] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        log_obj['_META_LOG_TYPE'] = log_type
        log_obj['_META_TITLE'] = log_title

        output = json.dumps(log_obj, ensure_ascii=False)

        if self.another_output_file != '':
            with open(self.another_output_file, 'a') as w:
                w.write(output + '\n')

        print(output, flush=True)
        # _service로는 에러메시지 보내면 안됨
        # 에러 모니터링 어떻게 하지...
        # if log_type == 'ERROR' or log_type == 'CRITICAL' or log_type == 'ALERT':
        #     fire(
        #         log_obj,
        #         keys=[ '_META_RUNNING_ENV', '_META_SERVICE_ID', '_META_DATETIME',
        #                 '_META_LOG_TYPE', '_META_DATETIME',
        #                 'error' ],
        #         kors= {
        #             'title': '아파트명',
        #             'jibeon_juso': '지번주소',
        #             'pre_loan_amount': '기존대출금액(만원)',
        #             'pre_deposit_amount': '전월세보증금(만원)',
        #             'assessment_amount': '감정가(만원)',
        #             'loan_limit_amount': '대출한도(만원)',
        #             'application_amount': '신청금액(만원)',
        #             'user_name': '신청자 이름',
        #             'user_phone': '연락처'
        #         }
        #     ) # 이거 비동기로 바꿔야 함


    def DEBUG(self, log_title, log_obj=None, request=None):
        if settings.DEBUG:
            self.write("DEBUG", log_title, self.make_log_json(log_obj, request))

    def INFO(self, log_title, log_obj=None, request=None):
        if self.verbose:
            self.write("INFO", log_title, self.make_log_json(log_obj, request))

    def WARNING(self, log_title, log_obj=None, request=None):
        self.write("WARNING", log_title, self.make_log_json(log_obj, request))

    def ERROR(self, log_title, log_obj=None, request=None):
        self.write("ERROR", log_title, self.make_log_json(log_obj, request))

    def CRITICAL(self, log_title, log_obj=None, request=None):
        self.write("CRITICAL", log_title, self.make_log_json(log_obj, request))

    def ALERT(self, log_title, log_obj=None, request=None):
        self.write("ALERT", log_title, self.make_log_json(log_obj, request))

    # https://api.slack.com/apps/APMAAS71A/oauth?success=1
    def send_slack(self, text):
        client = slack.WebClient(settings.SLACK_API_TOKEN)
        client.chat_postMessage(channel= '#pilot', text= text)

    def make_log_json(self, log_obj, request):
        ret = {}
        if log_obj is not None:
            ret = copy.deepcopy(log_obj)
        if request is not None:
            ret['username'] = request.user.username
            if ret['username'] == '':
                ret['username'] = 'anonymous_user'
                ret['email'] = ''
            else:
                ret['email'] = request.user.email
            ret['data'] = request.data
            # ret['query_params'] = request.query_params

        return json.dumps(ret, ensure_ascii=False)
