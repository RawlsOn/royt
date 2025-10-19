from django.conf import settings

from common.util.romsg import rp
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
from django.db import connection

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models import QuerySet
import common.util.datetime_util as dt_util
from common.util import curlreq

import common.util.datetime_util as datetime_util
import common.util.str_util as str_util
import common.util.juso_util as juso_util
from common.util.logger import RoLogger
logger = RoLogger()
from argparse import Namespace
from bs4 import BeautifulSoup
from django.apps import apps
import core.models as core_models
# from main.workers.ArticleHtmlGetter import ArticleHtmlGetter

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# ./manage.py run_article_detail_processor

LIMIT = 1000
class ArticleDetailProcessor(object):

    def __init__(self, args={}):
        self.args = args

    def run(self):
        print('run ArticleDetailProcessor', self.args)
        try:
            sido = self.args.sido
            model = apps.get_model('core', 'Article' + sido)
            self.model = model
            print('counting...')
            targets = model.objects.filter(
                has_detail_text= True,
                is_detail_processed= False,
                is_detail_failed= False,
            )
            self.total_count = targets.count()
            self.idx = 0
            while True:
                self.process()
        except Exception as e:
            if 'Lost connection to server during query' in str(e):
                rp('Lost connection to server during query')
                rp('sleep 10 min')
                time.sleep(600)
                return
            raise e

    def process(self):
        print('raw querying...')
        sido = self.args.sido
        model = apps.get_model('core', 'Article' + sido)
        targets = model.objects.raw(f"""
SELECT * FROM core_article{sido}
WHERE has_detail_text= 1 and is_detail_processed= 0 and is_detail_failed= 0
LIMIT {LIMIT};
            """
        )
        rp('processing detail... total_count: ')
        if len(targets) == 0:
            rp('nothing to do')
            rp('Wait 10 minutes...')
            time.sleep(600)
            return

        for target in targets:
            try:
                self._process(target)
            except Exception as e:
                print(str(e) + ' ' + target.article_id, target.created_date)
                to_print = target.__dict__
                del to_print['_state']
                del to_print['detail_text']
                pp.pprint(to_print)
                pp.pprint(self.doc)
                raise e
                target.is_processed = True
                target.is_processed_at = '1970-01-01'
                target.save()
                pass

    def _process(self, article):
        self.idx += 1
        str_util.print_progress(self.idx, self.total_count, gap= 10, info='process article detail...')
        # print('process', target.article_id, target.detail_text)
        result = self.parse(article)
        if result is None:
            article.is_detail_processed = True
            article.detail_processed_at = timezone.now()
            article.is_live = False
            article.is_live_checked_at = timezone.now()
            article.save()
            return

        original = article.__dict__

        is_dup, key, content = str_util.two_dict_dup_key_exist_and_diff_value(original, result)
        if is_dup:
            if key in ['tagList', '방향', '전용률', '건물_사용승인일', '노출시작일']:
                # 상세가 우선함
                pass
            else:
                test = {**original, **result}
                raise Exception(
                    'two_dict_dup_key_exist ' + key + ' ' + content + '\n' + test[key]
                )

        final = {**original, **result}
        del final['_state']
        # print('updating...')
        # pp.pprint(final)
        article = self.model(**final)
        article.is_detail_processed = True
        article.detail_processed_at = timezone.now()
        article.save()
        # print('end updating...')
        return article

    def parse(self, target):
        if target.detail_text is None:
            return {}
        _, splitted = target.detail_text.split('<script>window.App=')
        result = splitted.split('</script><script src')
        s_obj = json.loads(result[0])
        self.s_obj = s_obj
        # print(target.article_id)
        # pp.pprint(s_obj)

        # pp.pprint(s_obj['state']['article'])
        article = s_obj['state']['article']['article']
        building = s_obj['state']['article']['buildingRegister']
        location = s_obj['state']['article']['location']
        space = s_obj['state']['article']['space']
        facility = s_obj['state']['article']['facility']
        addition = s_obj['state']['article']['addition']
        floor = s_obj['state']['article']['floor']
        ground = s_obj['state']['article']['ground']
        price = s_obj['state']['article']['price']
        articleFacilities = s_obj['state']['articleFacilities']

        if article.get('articleConfirmYMD', None) is None:
            return {}

        self.doc = {}
        doc = self.doc
        # 중요정보
        # doc['날짜'] = article['articleConfirmYMD']
        # doc['공급면적'] = space['supplySpace']
        # doc['전용면적'] = space['exclusiveSpace']
        doc['전용률'] = space.get('exclusiveRate', None)
        if doc['전용률'] == '-':
            doc['전용률'] = None
        # 전용률이 백이 넘는 경우가 있음. 사용자가 전용률을 대충 넣은 경우 같음
        # https://m.land.naver.com/article/info/2330083090
        if doc['전용률'] and  doc['전용률'].isnumeric() and int(doc['전용률']) > 100:
            doc['전용률'] = None

        doc['융자금'] = price.get('financePrice', None)
        # doc['보증금'] = price['warrantPrice']
        # doc['임대료'] = price['rentPrice']

        doc['방향'] = facility.get('directionTypeName', None)
        # doc['중요설명'] = article['articleFeatureDescription']
        doc['상세설명'] = article.get('articleDescription', None)
        if doc['상세설명'] is None:
            doc['상세설명'] = article.get('detailDescription', None)
        doc['노출시작일'] = self.__split_날짜(article['exposeStartYMD'])

        doc['노출종료일'] = article['exposeEndYMD']
        year = article['exposeEndYMD'][:4]
        month = article['exposeEndYMD'][4:6]
        day = article['exposeEndYMD'][6:8]
        doc['노출종료일'] = year + '-' + month + '-' + day

        doc['기보증금'] = price.get('allWarrantPrice', None)
        doc['기월세'] = price.get('allRentPrice', None)
        doc['난방1'] = facility.get('heatMethodTypeName', None)
        doc['난방2'] = facility.get('heatFuelTypeName', None)
        doc['관리비'] = article.get('monthlyManagementCost', None)
        doc['냉방시설'] = facility.get('airconFacilities', None)
        if doc['냉방시설']:
            doc['냉방시설'] = ','.join(doc['냉방시설'])
        doc['건물_사용승인일'] = self.__split_날짜(facility.get('buildingUseAprvYmd', None))

        doc['지하철역_갯수'] = articleFacilities['subwayCount']
        doc['버스정류장_갯수'] = articleFacilities['busCount']
        doc['지하철역_도보시간_분'] = article['walkingTimeToNearSubway']
        doc['입주타입'] = article['moveInTypeName']
        doc['입주가능일'] = article.get('moveInPossibleYmd', None)
        if doc['입주가능일']:
            if doc['입주가능일'] == 'NOW':
                doc['입주가능일'] = '1970-01-01'
            else:
                doc['입주가능일'] = self.__split_날짜(doc['입주가능일'])

        doc['기타주소'] = article.get('etcAddress', None)
        doc['pnu'] = article.get('pnu', None)
        if doc['pnu'] is None:
            # print('pnu is None')
            # pp.pprint('building', building)
            doc['pnu'] = building.get('pnu', None)
            # print('PNU from building', doc['pnu'])

        # 생성정보
        doc['sido'] = location['cityName']
        doc['sgg'] = location['divisionName']
        doc['emd'] = location['sectionName']
        doc['jb'] = article.get('jibunAddress', '')

        # 지번에다가 이상한 걸 넣어놓는 경우가 있음
        # eg) 인천광역시 서구 서곶로90 루원프라자 제4층 제401호, 제402호 전체
        if len(doc['jb']) > 16:
            doc['bad_jb'] = doc['jb']
            doc['jb'] = 'BAD_CASE'
        if doc['jb']:
            # print('지번 있음-----------')
            doc['juso'] = ' '.join([
                doc['sido'], doc['sgg'], doc['emd'], doc['jb']
            ])
        else:
            # print('지번 없음------------')
            doc['juso'] = ' '.join([
                doc['sido'], doc['sgg'], doc['emd'], article['articleName'][:16]
            ])

        # PNu 없는 것은 아파트 단지 뿐인 듯. 일단 제낀다.
        # 상가에도 없는 경우가 있음. PNU는 나중에
        if not doc['pnu']:
            doc['pnu'] = 'XX_' + target.lat + '_' + target.lng
        #     print('PNU 없음-----------')
        #     juso_obj = juso_util.get_kakao_place(
        #         # doc['juso'],
        #         '서울시 광진구 뚝섬로 477',
        #         x= target.lng,
        #         y= target.lat
        #     )
        #     pp.pprint(juso_obj)

        # 별로 안 중요해보이는 정보
        doc['type1'] = article['articleName'][:64]
        doc['type2'] = article.get('buildingTypeName', None)
        doc['type3'] = article['realestateTypeName']
        doc['type4'] = article['tradeTypeName']
        doc['articleStatusCode'] = article['articleStatusCode']
        doc['articleTypeCode'] = article['articleTypeCode']
        doc['lawUsage'] = article.get('lawUsage', None)
        # print(doc)
        if article.get('moveindiscussionpossibleyn', None):
            doc['moveInDiscussionPossibleYN'] = article['moveInDiscussionPossibleYN'].upper() == 'Y'
        doc['moveInTypeCode'] = article['moveInTypeCode']
        doc['총_주차대수'] = article.get('parkingCount', None)
        doc['주차가능여부'] = article['parkingPossibleYN'].upper() == 'Y'
        doc['tagList'] = ','.join(article['tagList'])

        # 230819 신규
        doc['articleSubName'] = article.get('articleSubName', None)
        doc['tradeCompleteYN'] = article.get('tradeCompleteYN', '').upper() == 'Y'
        doc['총동갯수'] = article.get('totalDongCount', None)
        doc['directTradeYN'] = article.get('directTradeYN', '').upper() == 'Y'

        doc['방갯수'] = article.get('roomCount', None)
        if doc['방갯수'] == '':
            doc['방갯수'] = None
        if doc['방갯수']:
            doc['방갯수'] = int(doc['방갯수'])

        doc['화장실갯수'] = article.get('bathroomCount', None)
        if doc['화장실갯수'] == '' or doc['화장실갯수'] == '-':
            doc['화장실갯수'] = None
        if doc['화장실갯수']:
            doc['화장실갯수'] = int(doc['화장실갯수'])

        doc['건물이름'] = article.get('buildingName', None)
        doc['현재용도'] = article.get('currentUsage', None)
        doc['추천업종'] = article.get('recommendUsage', None)
        doc['duplexYN'] = article.get('duplexYN', '').upper() == 'Y'
        doc['floorLayerName'] = article.get('floorLayerName', None)
        doc['isComplex'] = article['isComplex']
        doc['floorInfo'] = addition['floorInfo']
        doc['priceChangeState'] = article.get('priceChangeState', None)
        doc['isPriceModification'] = article.get('isPriceModification', None)
        doc['cpName'] = article.get('cpName', None)

        self._process_종류별_거래타입별(target, s_obj)

        return doc

    def _process_종류별_거래타입별(self, target, s_obj):

        doc = self.doc
        if target.종류 == '토지':
            article = s_obj['state']['article']['article']
            ground = s_obj['state']['article']['ground']
            doc['토지_지역'] = ground.get('usageAreaTypeName', None)
            doc['토지_진입도로'] = ground.get('roadYN', None) == 'Y'
            doc['토지_현재용도'] = article.get('currentUsage', None)
            return

        # pp.pprint(s_obj)
        # pp.pprint(doc)
        # print(target.article_id)
        # raise ValueError(f'종류별({target.종류}) 거래타입별({target.거래타입}) 처리가 안되었습니다')

        # doc['난방1'] = facility['heatMethodTypeName']
        # doc['난방2'] = facility['heatFuelTypeName']

        # doc['관리비'] = article['monthlyManagementCost']


        # doc['건물_주용도'] = building['mainPurpsCdNm']
        # doc['건물_총_가구'] = building['fmlyCnt']
        # doc['건물_사용승인일'] = building['useAprDay']
        # doc['건물_층정보_지하'] = building['ugrndFlrCnt']
        # doc['건물_층정보_지상'] = building['grndFlrCnt']
        # doc['건물_주차장_옥내'] = building['indrAutoUtcnt']
        # doc['건물_주차장_옥외'] = building['oudrAutoUtcnt']
        # doc['건물_엘레베이터_비상'] = building['emgenUseElvtCnt']
        # doc['건물_엘레베이터_승용'] = building['rideUseElvtCnt']
    def __split_날짜(self, text):
        if text is None:
            return None
        text = text.strip()
        if len(text) == 4:
            return text + '-01-01'
        if text[:4] == '0000':
            return '1970-01-01'
        year = text[:4]
        month = text[4:6]
        day = text[6:8]
        if month == '00':
            month = '01'
        if len(month) == 1:
            month = '0' + month
        if day == '00':
            day = '01'

        if int(month) > 12:
            month = '12'

        final = year + '-' + month + '-' + day
        final = final.strip()
        if len(final) == 8 and final[-1] == '-':
            final = final + '01'
        return final
