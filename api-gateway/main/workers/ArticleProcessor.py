from django.conf import settings
from common.util.romsg import rp

import ast
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

from django.apps import apps

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models import QuerySet

import common.util.datetime_util as datetime_util
import common.util.str_util as str_util
from common.util.logger import RoLogger
logger = RoLogger()
from argparse import Namespace

import rawarticle.models as rawarticle_models
import core.models as core_models

PY_MULTI = 0.3025

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
class ArticleProcessor(object):

    def __init__(self, args={}):
        self.args = args

    def run(self):
        print('run ArticleProcessor', self.args)
        rp('counting...')
        rp('today : ' + str(timezone.now().date()))
        targets = rawarticle_models.ProtoArticle.objects.filter(
            created_date= timezone.now().date(),
            is_processed= False
        )
        self.total_count = targets.count()
        self.idx = 0
        while True:
            if self.total_count == 0:
                rp('No targets... All Job Done. Sleep 5 min')
                time.sleep(60 * 5)
                continue
            self.process()

    def process(self):
        print('start article processing...')
        targets = rawarticle_models.ProtoArticle.objects.filter(
            created_date= timezone.now().date(),
            is_processed= False
        )
        if targets.count() == 0:
            rp('No targets... All Job Done. Sleep 5 min')
            time.sleep(60 * 5)
            return

        self.total_count = targets.count()
        self.idx = 0

        rp('processing ' + str(self.total_count) + ' articles')
        gap = 1000
        from_idx = self.args.no * gap
        to_idx = (self.args.no + 1) * gap - 1
        print(from_idx, 'to', to_idx)
        targets = targets[from_idx:to_idx]

        for target in targets:
            str_util.print_progress(self.idx, self.total_count, gap= 10, info='process articles...')
            try:
                self._process(target)
            except Exception as e:
                # 임시로 그냥 다 처리함
                print(str(e) + ' ' + target.article_id, target.created_date)
                raise e
                target.is_processed = True
                target.is_processed_at = '1970-01-01'
                target.save()
                pass


    def _process(self, target):
        self.idx += 1
        # str_util.print_progress(self.idx, self.total_count, gap= 10, info='process articles...')

        # pp.pprint(target.to_obj)
        self.datum = {}
        # list_json = json.loads(target.list_text)
        list_json = ast.literal_eval(target.list_text)

        datum = self.datum
        datum['article_id'] = target.article_id

        datum['title'] = list_json['atclNm']
        datum['build_name'] = list_json.get('bildNm', None)
        datum['vrfcTpCd'] = list_json['vrfcTpCd']
        datum['rletTpNm'] = list_json['rletTpNm']

        atclCfmYmd = list_json.get('atclCfmYmd', None)
        if atclCfmYmd:
            datum['확인날짜'] = '20' + list_json['atclCfmYmd'].replace('.', '-')[:-1]
        datum['중요설명'] = list_json.get('atclFetrDesc', '')
        datum['종류'] = _get_type(list_json, 'rletTpNm')
        datum['거래타입'] = list_json['tradTpNm']
        datum['cortarNo'] = list_json['cortarNo']
        datum['lat'] = list_json['lat']
        datum['lng'] = list_json['lng']

        datum['sido'] = target.sido
        datum['sgg'] = target.sgg
        datum['emd'] = target.emd
        datum['lgeo'] = target.lgeo

        datum['tagList'] = ','.join(list_json['tagList'])

        if int(list_json['prc']) > 10000000: # 천억 이상
            datum['dev_memo'] = '천억 이상 / 오류일 확률이 높음'
            list_json['prc'] = int(list_json['prc']) / 10000

        self._process_종류별_거래타입별(list_json)

        if datum.get('공급면적_평', None) and datum['공급면적_평'] == '-':
            datum['공급면적_평'] = None

        if datum.get('전용면적_평', None) and datum['전용면적_평'] == '-':
            datum['전용면적_평'] = None

        datum['is_live'] = True
        datum['is_live_checked_at'] = target.created_at

        model = apps.get_model('core', 'Article' + target.sido)
        got, created = model.objects.get_or_create(
            article_id= datum['article_id'],
            defaults= datum
        )
        # 이미 아티클이 있을 경우
        if not created:
            # 기존 것을 히스토리에 넣는다
            history = got.to_obj
            # print('got.created_date', got.created_date)
            # history의 기준일은 Proto가 생성된 날
            history['gijun_date'] = target.created_date
            history['gijun_date_str'] = target.created_date
            # article의 히스토리에다 현재 상태를 저장
            # print(target.sido, '1------------------------')
            got.history_set.create(**history)
            # 새로운 데이터로 현재 article를 업데이트
            # 이렇게 세이브할 때는 auto 필드가 안되는 듯
            datum['created_date'] = got.created_date
            datum['created_at'] = got.created_at
            datum['updated_at'] = timezone.now()
            datum['has_history'] = True
            # print('2-----------------------------')
            model = apps.get_model('core', 'Article' + target.sido)
            # 기존의 아티클을 새로운 데이터로 업데이트한다
            got = model(**datum)
            got.save()

        target.is_processed = True
        target.processed_at = timezone.now()
        target.save()

    def __set_전용면적_values(self, 타입, list_json):
        datum = self.datum
        spc2 = list_json.get('spc2', None)
        if spc2:
            datum['전용면적_평'] = float(list_json['spc2']) * PY_MULTI
            if datum['전용면적_평'] > 1: # 1로 되어 있어서 오류나는 경우 있음
                datum['전용면적_평당_' + 타입] = (datum[타입] * 10000) / datum['전용면적_평']
                    # positive integer 최대값이 2^32 임
                    # 42.9억인데, 평당 가격이 이정도면 오류라고 봐야 함
                if datum['전용면적_평당_' + 타입] > 2**32:
                    datum['전용면적_평당_' + 타입] = None

    def __set_공급면적_values(self, 타입, list_json):
        datum = self.datum
        spc1 = list_json.get('spc1', None)
        if spc1:
            if spc1 == '-':
                datum['공급면적_평'] = None
            else:
                datum['공급면적_평'] = float(list_json['spc1']) * PY_MULTI
                if datum['공급면적_평'] > 1: # 1로 되어 있어서 오류나는 경우 있음
                    datum['공급면적_평당_' + 타입] = (datum[타입] * 10000) / datum['공급면적_평']
                    # positive integer 최대값이 2^32 임
                    # 42.9억인데, 평당 가격이 이정도면 오류라고 봐야 함
                    if datum['공급면적_평당_' + 타입] > 2**32:
                        datum['공급면적_평당_' + 타입] = None


    def _process_종류별_거래타입별(self, list_json):
        datum = self.datum
        if datum['종류'] == '아파트' and datum['거래타입'] == '매매':
            datum['방향'] = list_json.get('direction', None)
            datum['매매가'] = list_json['prc']
            self.__set_공급면적_values('매매가', list_json)
            self.__set_전용면적_values('매매가', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '아파트' and datum['거래타입'] == '전세':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            self.__set_공급면적_values('보증금', list_json)
            self.__set_전용면적_values('보증금', list_json)

            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '아파트' and datum['거래타입'] == '월세':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            self.__set_공급면적_values('임대료', list_json)
            self.__set_전용면적_values('임대료', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '아파트' and datum['거래타입'] == '단기임대':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            self.__set_공급면적_values('임대료', list_json)
            self.__set_전용면적_values('임대료', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '오피스텔/빌라' and datum['거래타입'] == '매매':
            datum['방향'] = list_json.get('direction', None)
            datum['매매가'] = list_json['prc']
            self.__set_공급면적_values('매매가', list_json)
            self.__set_전용면적_values('매매가', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '오피스텔/빌라' and datum['거래타입'] == '전세':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']

            self.__set_공급면적_values('보증금', list_json)
            self.__set_전용면적_values('보증금', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '오피스텔/빌라' and datum['거래타입'] == '월세':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            self.__set_공급면적_values('임대료', list_json)
            self.__set_전용면적_values('임대료', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '오피스텔/빌라' and datum['거래타입'] == '단기임대':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            self.__set_공급면적_values('임대료', list_json)
            self.__set_전용면적_values('임대료', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '원룸/고시원' and datum['거래타입'] == '전세':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            self.__set_공급면적_values('보증금', list_json)
            self.__set_전용면적_values('보증금', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '원룸/고시원' and datum['거래타입'] == '월세':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            self.__set_공급면적_values('임대료', list_json)
            self.__set_전용면적_values('임대료', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '원룸/고시원' and datum['거래타입'] == '단기임대':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            self.__set_공급면적_values('임대료', list_json)
            self.__set_전용면적_values('임대료', list_json)
            if list_json.get('flrInfo', None) is not None:
                datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '건물' and datum['거래타입'] == '매매':
            datum['방향'] = list_json.get('direction', None)
            datum['매매가'] = list_json['prc']
            self.__set_공급면적_values('매매가', list_json)
            self.__set_전용면적_values('매매가', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '건물' and datum['거래타입'] == '전세':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']

            self.__set_공급면적_values('보증금', list_json)
            self.__set_전용면적_values('보증금', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '건물' and datum['거래타입'] == '월세':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            self.__set_공급면적_values('임대료', list_json)
            self.__set_전용면적_values('임대료', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '건물' and datum['거래타입'] == '단기임대':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            self.__set_공급면적_values('임대료', list_json)
            self.__set_전용면적_values('임대료', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '상가' and datum['거래타입'] == '매매':
            datum['방향'] = list_json.get('direction', None)
            datum['매매가'] = list_json['prc']
            self.__set_공급면적_values('매매가', list_json)
            self.__set_전용면적_values('매매가', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '상가' and datum['거래타입'] == '전세':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            self.__set_공급면적_values('보증금', list_json)
            self.__set_전용면적_values('보증금', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '상가' and datum['거래타입'] == '월세':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            self.__set_공급면적_values('임대료', list_json)
            self.__set_전용면적_values('임대료', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '상가' and datum['거래타입'] == '단기임대':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            self.__set_공급면적_values('임대료', list_json)
            self.__set_전용면적_values('임대료', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '재건축/재개발' and datum['거래타입'] == '매매':
            datum['방향'] = list_json.get('direction', None)
            datum['매매가'] = list_json['prc']
            self.__set_공급면적_values('매매가', list_json)
            self.__set_전용면적_values('매매가', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '재건축/재개발' and datum['거래타입'] == '전세':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            self.__set_공급면적_values('보증금', list_json)
            self.__set_전용면적_values('보증금', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '재건축/재개발' and datum['거래타입'] == '월세':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            self.__set_공급면적_values('임대료', list_json)
            self.__set_전용면적_values('임대료', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '재건축/재개발' and datum['거래타입'] == '단기임대':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            self.__set_공급면적_values('임대료', list_json)
            self.__set_전용면적_values('임대료', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '분양권' and datum['거래타입'] == '매매':
            datum['방향'] = list_json.get('direction', None)
            datum['매매가'] = list_json['prc']
            self.__set_공급면적_values('매매가', list_json)
            self.__set_전용면적_values('매매가', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '분양권' and datum['거래타입'] == '전세':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            self.__set_공급면적_values('보증금', list_json)
            self.__set_전용면적_values('보증금', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '분양권' and datum['거래타입'] == '월세':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            self.__set_공급면적_values('임대료', list_json)
            self.__set_전용면적_values('임대료', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '분양권' and datum['거래타입'] == '단기임대':
            datum['방향'] = list_json.get('direction', None)
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            self.__set_공급면적_values('임대료', list_json)
            self.__set_전용면적_values('임대료', list_json)
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '토지' and datum['거래타입'] == '매매':
            datum['매매가'] = list_json['prc']
            datum['면적_평'] = float(list_json['spc1'])
            datum['평당_매매가'] = datum['매매가'] / datum['면적_평']
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '토지' and datum['거래타입'] == '전세':
            datum['보증금'] = list_json['prc']
            datum['면적_평'] = float(list_json['spc1'])
            datum['평당_보증금'] = datum['보증금'] / datum['면적_평']
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '토지' and datum['거래타입'] == '월세':
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            datum['면적_평'] = float(list_json['spc1'])
            datum['평당_임대료'] = datum['임대료'] / datum['면적_평']
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        if datum['종류'] == '토지' and datum['거래타입'] == '단기임대':
            datum['보증금'] = list_json['prc']
            datum['임대료'] = list_json['rentPrc']
            datum['면적_평'] = float(list_json['spc1'])
            datum['평당_임대료'] = datum['임대료'] / datum['면적_평']
            datum['층'], datum['한글층'], datum['총층'] = self.__get_층(list_json['flrInfo'])
            return

        print(list_json)
        pp.pprint(datum)
        raise ValueError(f'종류별({datum["종류"]}) 거래타입별({datum["거래타입"]}) 처리가 안되었습니다')

    def get_detail(self, target):
        print(target.to_obj)
        print(target.created_date)

    def __get_층(self, flrInfo):
            if flrInfo == '-':
                return None, None, None

            datum = {}
            datum['한글층'] = None
            층 = flrInfo.split('/')[0]
            if 층[0] == 'B':
                datum['층'] = 층.replace('B', '-')
            datum['층'] = 층.isnumeric() and int(층) or None
            if datum['층'] is None:
                datum['한글층'] = 층
            datum['총층'] = flrInfo.split('/')[1]
            if datum['총층'] == '-':
                datum['총층'] = None
            if datum['총층'] and datum['총층'][0] == 'B':
                datum['총층'] = datum['총층'].replace('B', '-')
            return datum['층'], datum['한글층'], datum['총층']



def _get_type(article, key):
    ret = ''
    datum = article[key]
    if datum in ['상가', '사무실']:
        ret = '상가'
    elif datum in [
        '전원주택', '단독/다가구', '상가주택', '한옥주택',
        '공장/창고', '건물'
    ]:
        ret = '건물'
    elif datum in ['토지']:
        ret = '토지'
    elif datum in [
        '아파트'
    ]:
        ret = '아파트'
    elif datum in [
        '오피스텔', '빌라'
    ]:
        ret = '오피스텔/빌라'
    elif datum in [
        '아파트분양권', '오피스텔분양권'
    ]:
        ret = '분양권'
    elif datum in [
        '재건축', '재개발',
    ]:
        ret = '재건축/재개발'
    elif datum in [
        '원룸', '고시원',
        # 고시원 샘플 : https://m.roomnspace.co.kr/gosiwon/detail/6949
    ]:
        ret = '원룸/고시원'
    elif datum in [
        '지식산업센터'
    ]:
        ret = '지식산업센터'

    return ret