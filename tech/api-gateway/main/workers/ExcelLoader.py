from django.conf import settings

import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

from common.util import juso_util, model_util, str_util
from django.contrib.gis.geos import Point

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone

import openpyxl

import geoinfo.models as geoinfo_models
import main.models as main_models
import core.models as core_models
import user.models as user_models

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

class ExcelLoader(object):

    def __init__(self, args={}):
        self.args = args

    def run(self):
        print('run ExcelLoader', self.args)
        self.raw_data = {}
        self.groom_data = {}
        self.excel_doc = openpyxl.load_workbook(self.args.file_path)
        for sheet_name in self.excel_doc.get_sheet_names():
            self.load_sheet(sheet_name)
        self._update_db()

    def load_sheet(self, sheet_name):
        self.load_raw(sheet_name)
        if sheet_name == '토지':
            self.groom_토지()
            self.load_to_db_토지()
        if sheet_name == '건물':
            self.groom_건물()
            self.load_to_db_건물()
        if sheet_name == '상가':
            self.groom_상가()
            self.load_to_db_상가()

    def load_raw(self, sheet_name):
        print('sheet_name', sheet_name)
        raw_result = []
        sheet = self.excel_doc.get_sheet_by_name(sheet_name)
        all_rows = sheet.rows
        idx = 0
        titles = []
        for row in all_rows:
            # print('row', idx, row, 'row[0].value', row[0].value)
            # print(idx, [x.value for x in row])

            idx += 1
            if idx == 1:
                titles = []
                for x in row:
                    if x.value:
                        titles.append(x.value.strip())
                continue

            if sheet_name == '상가' and idx < 8: # 엑셀파일보고 하드코딩
                idx += 1
                continue

            if row[0].value is None and row[1].value is None:
                idx += 1
                continue

            raw_datum = {}
            jdx = -1
            for cell in row:
                jdx += 1
                if jdx >= len(titles): continue
                if titles[jdx] is None: continue
                raw_datum[titles[jdx]] = cell.value
            raw_result.append(raw_datum)

        self.raw_data[sheet_name] = raw_result
        self.groom_data[sheet_name] = []

    def groom_토지(self):
        for datum in self.raw_data['토지']:
            if datum['주소'] is None:
                continue

            datum['주소'] = datum['주소'].strip()

            ret = {}
            month = str(datum['날짜(월)'])
            if len(month) == 1:
                month = '0' + month

            ret['기준일자'] = str(datum['날짜(년)']) + '-' + month + '-' + self.args.upload_day
            ret['지번주소'] = datum['주소']
            ret['추가주소'] = datum['추가주소']

            ret['용도지역'] = datum['용도지역'].strip()
            ret['지목'] = datum['지목'].strip()

            ret['토지면적_제곱미터'] = datum['토지면적(㎡)']
            ret['토지면적_평'] = None
            try:
                ret['토지면적_평'] = int(datum['토지면적(평)'])
            except Exception as e:
                ret['토지면적_평'] = ret['토지면적_제곱미터'] * 0.3025

            if not ret['토지면적_평'] and ret['토지면적_제곱미터']:
                ret['토지면적_평'] = ret['토지면적_제곱미터'] * 0.3025

            if not ret['토지면적_제곱미터'] and ret['토지면적_평']:
                ret['토지면적_제곱미터'] = ret['토지면적_평'] / 0.3025

            if ret['토지면적_평']:
                ret['토지면적_평'] = round(ret['토지면적_평'], 4)

            if ret['토지면적_제곱미터']:
                ret['토지면적_제곱미터'] = round(ret['토지면적_제곱미터'], 4)

            ret['매매가'] = datum['매매가(만원)']
            if ret['매매가']:
                ret['매매가'] = ret['매매가'] * 10000

            ret['평당가격'] = datum['평당가격(만원)']
            if isinstance(ret['평당가격'], str) and ret['평당가격'][0:3] == '=IF':
                ret['평당가격'] = None
            if ret['평당가격']:
                ret['평당가격'] = ret['평당가격'] * 10000
            if not ret['평당가격'] and ret['매매가']:
                ret['평당가격'] = ret['매매가'] / ret['토지면적_평']

            if ret['평당가격']:
                ret['제곱미터당가격'] = ret['매매가'] / ret['토지면적_제곱미터']

            ret['기타사항'] = datum['기타사항']
            if ret['기타사항']:
                ret['기타사항'] = str(ret['기타사항']).strip()

            self.groom_data['토지'].append(ret)

    def load_to_db_토지(self):
        total_count = len(self.groom_data['토지'])
        admin = user_models.CustomUser.objects.get(email= self.args.admin_email)
        for idx, datum in enumerate(self.groom_data['토지']):
            str_util.print_progress(idx, total_count, gap= 10, info='create 토지...')
            geo_unit = None
            if datum.get('추가주소', None):
                geo_unit = self._get_geo_unit_추가주소(datum)
            else:
                geo_unit = self._get_geo_unit(datum)

            if geo_unit:
                토지, created = core_models.토지.objects.get_or_create(
                    geo_unit_id= geo_unit.id,
                    토지면적_평= datum['토지면적_평'],
                    지번주소_cp= datum['지번주소'],
                    defaults= {
                        'uploader_id': admin.id,
                        '토지면적_제곱미터': datum['토지면적_제곱미터'],
                        '용도지역': datum['용도지역'],
                        '지목': datum['지목'],
                    }
                )

                토지매물, created = core_models.토지매물.objects.get_or_create(
                    토지= 토지,
                    기준일자_str= datum['기준일자'],
                    defaults= {
                        'uploader_id': admin.id,
                        '기준일자': datum['기준일자'],
                        '매매가': datum['매매가'],
                        '평당가격': datum['평당가격'],
                        '제곱미터당가격': datum['제곱미터당가격'],
                        '지번주소_cp': datum['지번주소'],
                    }
                )

                if created and datum['기타사항']:
                    main_models.토지매물노트.objects.create(
                        user= admin,
                        토지매물_id= 토지매물.id,
                        content= datum['기타사항']
                    )

    def groom_건물(self):
        for datum in self.raw_data['건물']:
            # print(datum)
            if datum['주소'] is None:
                continue

            datum['주소'] = datum['주소'].strip()

            ret = {}
            month = str(datum['날짜(월)'])
            if len(month) == 1:
                month = '0' + month

            ret['기준일자'] = str(datum['날짜(년)']) + '-' + month + '-' + self.args.upload_day
            ret['지번주소'] = datum['주소']
            ret['추가주소'] = datum['추가주소']

            ret['용도지역'] = datum['용도지역']

            ret['토지면적_제곱미터'] = datum['토지면적(㎡)']
            if isinstance(ret['토지면적_제곱미터'], str) and ret['토지면적_제곱미터'][0] == '=':
                # =45*3.3 이런 식으로 들어가 있는 게 있음
                ret['토지면적_제곱미터'] = eval(ret['토지면적_제곱미터'][1:])
            ret['토지면적_평'] = None
            try:
                ret['토지면적_평'] = int(datum['토지면적(평)'])
            except Exception as e:
                # print(ret, e)
                ret['토지면적_평'] = ret['토지면적_제곱미터'] * 0.3025
            if not ret['토지면적_평'] and ret['토지면적_제곱미터']:
                ret['토지면적_평'] = ret['토지면적_제곱미터'] * 0.3025

            if not ret['토지면적_제곱미터'] and ret['토지면적_평']:
                ret['토지면적_제곱미터'] = ret['토지면적_평'] / 0.3025

            ret['건물용도'] = datum['건물 용도']
            if ret['건물용도']:
                ret['건물용도'] = ret['건물용도'].strip()

            ret['연면적_제곱미터'] = datum['연면적(㎡)']
            if isinstance(ret['연면적_제곱미터'], str) and ret['연면적_제곱미터'][0] == '=':
                # =45*3.3 이런 식으로 들어가 있는 게 있음
                ret['연면적_제곱미터'] = eval(ret['연면적_제곱미터'][1:])
            ret['연면적_평'] = None
            try:
                ret['연면적_평'] = int(datum['연면적(평)'])
            except Exception as e:
                # print(ret, e)
                if ret['연면적_제곱미터']:
                    ret['연면적_평'] = ret['연면적_제곱미터'] * 0.3025
            if not ret['연면적_평'] and ret['연면적_제곱미터']:
                ret['연면적_평'] = ret['연면적_제곱미터'] * 0.3025

            if not ret['연면적_제곱미터'] and ret['연면적_평']:
                ret['연면적_제곱미터'] = ret['연면적_평'] / 0.3025

            if ret['토지면적_평']:
                ret['토지면적_평'] = round(ret['토지면적_평'], 4)

            if ret['토지면적_제곱미터']:
                ret['토지면적_제곱미터'] = round(ret['토지면적_제곱미터'], 4)

            if ret['연면적_평']:
                ret['연면적_평'] = round(ret['연면적_평'], 4)

            if ret['연면적_제곱미터']:
                ret['연면적_제곱미터'] = round(ret['연면적_제곱미터'], 4)

            ret['층_최저'] = datum['층(최저)']
            if ret['층_최저']:
                try:
                    # str일 경우 이게 되고 안되면 exception
                    if 'B' in ret['층_최저'].upper():
                        ret['층_최저'] = ret['층_최저'].replace('B', '-').replace('b', '-')
                    if 'F' in ret['층_최저'].upper():
                        ret['층_최저'] = ret['층_최저'].replace('F', '').replace('f', '')
                except Exception as e:
                    pass

            ret['층_최고'] = datum['층(최고)']
            if ret['층_최고']:
                try:
                    # str일 경우 이게 되고 안되면 exception
                    if 'B' in ret['층_최고'].upper():
                        ret['층_최고'] = ret['층_최고'].replace('B', '-').replace('b', '-')
                    if 'F' in ret['층_최고'].upper():
                        ret['층_최고'] = ret['층_최고'].replace('F', '').replace('f', '')
                except Exception as e:
                    pass

            ret['엘리베이터'] = datum['엘리베이터 유/무']
            ret['준공년도'] = datum['준공년도']

            ret['매매가'] = datum['매매가(만원)']
            # print(ret['매매가'][0:5])
            if isinstance(ret['매매가'], str) and ret['매매가'][0] == '-':
                ret['매매가'] = None
            if ret['매매가']:
                ret['매매가'] = ret['매매가'] * 10000

            ret['토지평당가격'] = datum['토지평당가격(만원)']
            ret['토지제곱미터당가격'] = None
            if isinstance(ret['토지평당가격'], str) and ret['토지평당가격'][0:3] == '=IF':
                ret['토지평당가격'] = None
            if ret['토지평당가격']:
                ret['토지평당가격'] = ret['토지평당가격'] * 10000
            if not ret['토지평당가격'] and ret['매매가']:
                # print(ret)
                ret['토지평당가격'] = ret['매매가'] / ret['토지면적_평']
            if ret['토지평당가격']:
                ret['토지제곱미터당가격'] = ret['매매가'] / ret['토지면적_제곱미터']

            ret['건물전체_보증금'] = datum['건물전체보증금(만원)']
            if ret['건물전체_보증금']:
                ret['건물전체_보증금'] = ret['건물전체_보증금'] * 10000

            ret['건물전체_임대료'] = datum['건물전체임대료(만원)']
            if ret['건물전체_임대료']:
                ret['건물전체_임대료'] = ret['건물전체_임대료'] * 10000

            ret['연면적_평당_임대료'] = None
            if ret['건물전체_임대료'] and ret['연면적_평']:
                ret['연면적_평당_임대료'] = ret['건물전체_임대료'] / ret['연면적_평']

            ret['연면적_제곱미터당_임대료'] = None
            if ret['건물전체_임대료'] and ret['연면적_제곱미터']:
                ret['연면적_제곱미터당_임대료'] = ret['건물전체_임대료'] / ret['연면적_제곱미터']

            ret['수익률'] = None
            if ret['건물전체_임대료'] and ret['매매가'] and ret['건물전체_보증금']:
                ret['수익률'] = ret['건물전체_임대료'] * 12 / (ret['매매가'] - ret['건물전체_보증금']) * 100

            ret['공용평당_관리비_원'] = datum['공용평당 관리비(원)']
            if isinstance(ret['공용평당_관리비_원'], str) and ret['공용평당_관리비_원'][0] == '=':
                # =45*3.3 이런 식으로 들어가 있는 게 있음
                ret['공용평당_관리비_원'] = eval(ret['공용평당_관리비_원'][1:])

            ret['공용제곱미터당_관리비_원'] = None
            if ret['공용평당_관리비_원']:
                ret['공용제곱미터당_관리비_원'] = ret['공용평당_관리비_원'] * 0.3025

            ret['지번주소_cp'] = datum['주소'].strip()
            ret['기타사항'] = datum['기타사항']
            if ret['기타사항']:
                ret['기타사항'] = str(ret['기타사항']).strip()

            self.groom_data['건물'].append(ret)

    def load_to_db_건물(self):
        total_count = len(self.groom_data['건물'])
        admin = user_models.CustomUser.objects.get(email= self.args.admin_email)
        for idx, datum in enumerate(self.groom_data['건물']):
            str_util.print_progress(idx, total_count, gap= 10, info='create 건물...')
            geo_unit = None
            if datum.get('추가주소', None):
                geo_unit = self._get_geo_unit_추가주소(datum)
            else:
                geo_unit = self._get_geo_unit(datum)

            if geo_unit:
                건물, created = core_models.건물.objects.get_or_create(
                    geo_unit_id= geo_unit.id,
                    연면적_평= datum['연면적_평'],
                    지번주소_cp= datum['지번주소'],
                    defaults= {
                        'uploader_id': admin.id,
                        '용도지역': datum['용도지역'],
                        '토지면적_제곱미터': datum['토지면적_제곱미터'],
                        '토지면적_평': datum['토지면적_평'],
                        '건물용도': datum['건물용도'],
                        '연면적_제곱미터': datum['연면적_제곱미터'],
                        '층_최고': datum['층_최고'],
                        '층_최저': datum['층_최저'],
                        '엘리베이터': datum['엘리베이터'],
                        '준공년도': datum['준공년도'],
                    }
                )

                건물매물, created = core_models.건물매물.objects.get_or_create(
                    건물= 건물,
                    기준일자_str= datum['기준일자'],
                    defaults= {
                        'uploader_id': admin.id,
                        '기준일자': datum['기준일자'],
                        '토지평당가격': datum['토지평당가격'],
                        '토지제곱미터당가격': datum['토지제곱미터당가격'],
                        '매매가': datum['매매가'],
                        '건물전체_보증금': datum['건물전체_보증금'],
                        '건물전체_임대료': datum['건물전체_임대료'],
                        '연면적_평당_임대료': datum['연면적_평당_임대료'],
                        '연면적_제곱미터당_임대료': datum['연면적_제곱미터당_임대료'],

                        '수익률': datum['수익률'],

                        '공용평당_관리비_원': datum['공용평당_관리비_원'],
                        '공용제곱미터당_관리비_원': datum['공용제곱미터당_관리비_원'],

                        '지번주소_cp': datum['지번주소'],
                    }
                )

                if created and datum['기타사항']:
                    main_models.건물매물노트.objects.create(
                        user= admin,
                        건물매물_id= 건물매물.id,
                        content= datum['기타사항']
                    )

    def groom_상가(self):
        for datum in self.raw_data['상가']:
            if datum['주소'] is None:
                continue

            datum['주소'] = datum['주소'].strip()

            ret = {}
            month = str(datum['날짜(월)'])
            if len(month) == 1:
                month = '0' + month

            ret['기준일자'] = str(datum['날짜(년)']) + '-' + month + '-' + self.args.upload_day
            ret['지번주소'] = datum['주소']
            ret['매매가'] = datum['매매가(만원)']

            ret['매매가'] = datum['매매가(만원)']
            # print(ret['매매가'][0:5])
            if isinstance(ret['매매가'], str) and ret['매매가'][0] == '-':
                ret['매매가'] = None
            if ret['매매가']:
                ret['매매가'] = ret['매매가'] * 10000

            ret['보증금'] = datum['보증금(만원)']
            if not ret['보증금']:
                ret['보증금'] = 0
            if ret['보증금']:
                ret['보증금'] = ret['보증금'] * 10000

            ret['임대료'] = datum['임대료(만원)']
            if ret['임대료']:
                ret['임대료'] = ret['임대료'] * 10000

            ret['수익률'] = None
            if ret['임대료'] and ret['매매가']:
                ret['수익률'] = (ret['임대료'] * 12) / (ret['매매가'] - ret['보증금']) * 100

            ret['권리금'] = datum['권리금(만원)']
            if ret['권리금']:
                ret['권리금'] = ret['권리금'] * 10000

            ret['공용평당_관리비_원'] = datum['공용평당 관리비(원)']
            if isinstance(ret['공용평당_관리비_원'], str) and ret['공용평당_관리비_원'][0] == '=':
                # =45*3.3 이런 식으로 들어가 있는 게 있음
                ret['공용평당_관리비_원'] = eval(ret['공용평당_관리비_원'][1:])

            ret['공용제곱미터당_관리비_원'] = None
            if ret['공용평당_관리비_원']:
                ret['공용제곱미터당_관리비_원'] = ret['공용평당_관리비_원'] * 0.3025

            ret['업종'] = datum['업종(상호 노출 금지)']
            ret['노출도'] = datum['노출도(노출, 내부, 코너)']
            ret['엘리베이터'] = datum['엘리베이터']

            ret['전용면적_제곱미터'] = datum['전용면적(㎡)']
            if isinstance(ret['전용면적_제곱미터'], str) and ret['전용면적_제곱미터'][0] == '=':
                # =45*3.3 이런 식으로 들어가 있는 게 있음
                ret['전용면적_제곱미터'] = eval(ret['전용면적_제곱미터'][1:])

            ret['전용면적_평'] = None
            try:
                ret['전용면적_평'] = int(datum['전용면적(평)'])
            except Exception as e:
                # print(ret, e)
                ret['전용면적_평'] = ret['전용면적_제곱미터'] * 0.3025
            if not ret['전용면적_평'] and ret['전용면적_제곱미터']:
                ret['전용면적_평'] = ret['전용면적_제곱미터'] * 0.3025

            if not ret['전용면적_제곱미터'] and ret['전용면적_평']:
                ret['전용면적_제곱미터'] = ret['전용면적_평'] / 0.3025

            if ret['전용면적_평']:
                ret['전용면적_평'] = round(ret['전용면적_평'], 4)

            if ret['전용면적_제곱미터']:
                ret['전용면적_제곱미터'] = round(ret['전용면적_제곱미터'], 4)

            ret['준공년도'] = datum['준공년도']
            ret['층'] = datum['층']
            if ret['층']:
                try:
                    # str일 경우 이게 되고 안되면 exception
                    if 'B' in ret['층'].upper():
                        ret['층'] = ret['층'].replace('B', '-').replace('b', '-')
                    if 'F' in ret['층'].upper():
                        ret['층'] = ret['층'].replace('F', '').replace('f', '')
                    if len(ret['층'].split(',')) > 0:
                        ret['층'] = ret['층'].split(',')[0]
                except Exception as e:
                    pass

            ret['평당_임대료'] = None
            ret['제곱미터당_임대료'] = None
            if ret['임대료']:
                ret['평당_임대료'] = ret['임대료'] / ret['전용면적_평']
                ret['제곱미터당_임대료'] = ret['임대료'] / ret['전용면적_제곱미터']

            ret['호수'] = datum.get('호수', None)

            ret['기타사항'] = datum['기타사항']
            if ret['기타사항']:
                ret['기타사항'] = str(ret['기타사항']).strip()

            self.groom_data['상가'].append(ret)

    def load_to_db_상가(self):
        total_count = len(self.groom_data['상가'])
        admin = user_models.CustomUser.objects.get(email= self.args.admin_email)
        for idx, datum in enumerate(self.groom_data['상가']):
            str_util.print_progress(idx, total_count, gap= 10, info='create 상가...')
            geo_unit = self._get_geo_unit(datum)

            if geo_unit:
                상가, created = core_models.상가.objects.get_or_create(
                    geo_unit_id= geo_unit.id,
                    전용면적_평= datum['전용면적_평'],
                    노출도= datum['노출도'],
                    층= datum['층'],
                    defaults= {
                        'uploader_id': admin.id,
                        '전용면적_제곱미터': datum['전용면적_제곱미터'],
                        '엘리베이터': datum['엘리베이터'],
                        '준공년도': datum['준공년도'],
                        '호수': datum['호수'],
                        '지번주소_cp': datum['지번주소']
                    }
                )

                상가매물, created = core_models.상가매물.objects.get_or_create(
                    상가= 상가,
                    기준일자_str= datum['기준일자'],
                    defaults= {
                        'uploader_id': admin.id,
                        '기준일자': datum['기준일자'],
                        '업종': datum['업종'],
                        '매매가': datum['매매가'],
                        '보증금': datum['보증금'],
                        '임대료': datum['임대료'],
                        '권리금': datum['권리금'],
                        '공용평당_관리비_원': datum['공용평당_관리비_원'],
                        '공용제곱미터당_관리비_원': datum['공용제곱미터당_관리비_원'],
                        '수익률': datum['수익률'],
                        '평당_임대료': datum['평당_임대료'],
                        '제곱미터당_임대료': datum['제곱미터당_임대료'],
                        '지번주소_cp': datum['지번주소']
                    }
                )

                if created and datum['기타사항']:
                    main_models.상가매물노트.objects.create(
                        user= admin,
                        상가매물_id= 상가매물.id,
                        content= datum['기타사항']
                    )

    def _get_geo_unit(self, datum):
        지번주소 = datum['지번주소'].strip()
        geo_unit = model_util.get_or_none(geoinfo_models.GeoUnit, 주소_input= 지번주소)
        if not geo_unit:
            geo_unit = model_util.get_or_none(geoinfo_models.GeoUnit, uniq_title= 지번주소)
            if not geo_unit:
                k_juso_obj, success = juso_util.get_kakao_juso(지번주소)
                if success:
                    geo_unit, created = geoinfo_models.GeoUnit.objects.get_or_create(
                            주소_input= datum['지번주소'],
                            uniq_title= k_juso_obj['지번주소'],
                            defaults= {
                                '지번주소': k_juso_obj['지번주소'],
                                '도로명주소': k_juso_obj['도로명주소'],
                                'pnu': k_juso_obj['pnu'],
                                '시도': k_juso_obj['시도'],
                                '시군구': k_juso_obj['시군구'],
                                '읍면동': k_juso_obj['읍면동'],
                                '산': k_juso_obj['산'],
                                '본번': k_juso_obj['본번'],
                                '부번': k_juso_obj['부번'],
                                '지하': k_juso_obj['지하'],
                                'zone_no': k_juso_obj['zone_no'],
                                'point': k_juso_obj['point'],
                                'center': k_juso_obj['center'],
                            }
                        )
        return geo_unit

    def _get_geo_unit_추가주소(self, datum):
        추가주소 = datum['추가주소']
        all_jusos = [datum['지번주소']] + [x.strip() for x in 추가주소.split(',')]

        geo_unit_list = []
        for juso in all_jusos:
            geo_unit = model_util.get_or_none(geoinfo_models.GeoUnit, 주소_input= juso)
            if not geo_unit:
                k_juso_obj, success = juso_util.get_kakao_juso(juso)
                if success:
                    geo_unit, created = geoinfo_models.GeoUnit.objects.get_or_create(
                            주소_input= juso,
                            uniq_title= k_juso_obj['지번주소'],
                            defaults= {
                                '지번주소': k_juso_obj['지번주소'],
                                '도로명주소': k_juso_obj['도로명주소'],
                                'pnu': k_juso_obj['pnu'],
                                '시도': k_juso_obj['시도'],
                                '시군구': k_juso_obj['시군구'],
                                '읍면동': k_juso_obj['읍면동'],
                                '산': k_juso_obj['산'],
                                '본번': k_juso_obj['본번'],
                                '부번': k_juso_obj['부번'],
                                '지하': k_juso_obj['지하'],
                                'zone_no': k_juso_obj['zone_no'],
                                'point': k_juso_obj['point'],
                                'center': k_juso_obj['center'],
                            }
                        )
            if geo_unit:
                geo_unit_list.append(geo_unit)

        all_x_center = sum(map(lambda o: o.point.x, geo_unit_list)) / len(geo_unit_list)
        all_y_center = sum(map(lambda o: o.point.y, geo_unit_list)) / len(geo_unit_list)
        geo_unit, created = geoinfo_models.GeoUnit.objects.get_or_create(
            주소_input= ','.join(all_jusos),
            uniq_title= ','.join(all_jusos),
            defaults= {
                'point':Point(x= all_x_center, y= all_y_center),
                'center':Point(x= all_x_center, y= all_y_center)
            }
        )
        return geo_unit

    def _update_db(self):
        total = geoinfo_models.GeoUnit.objects.all().count()
        idx = 0
        for datum in geoinfo_models.GeoUnit.objects.all():
            idx += 1
            str_util.print_progress(idx, total, gap= 10, info='update  geo unit stat...')
            datum.토지_count = core_models.토지.objects.filter(geo_unit_id= datum.id).count()
            datum.건물_count = core_models.건물.objects.filter(geo_unit_id= datum.id).count()
            datum.상가_count = core_models.상가.objects.filter(geo_unit_id= datum.id).count()
            datum.total_물건_count = datum.토지_count + datum.건물_count + datum.상가_count
            datum.save()
