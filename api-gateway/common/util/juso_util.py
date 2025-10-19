# edit at 2024-05-20
# cp /Users/kimmyounghoon/Works/mkay/common/api-gateway/common/util/* ./api-gateway/common/util/

# git update-index --skip-worktree api-gateway/common/util/juso_util.py
# git update-index --skip-worktree api-gateway/common/util/RoPrinter.py
# git update-index --skip-worktree api-gateway/common/util/datetime_util.py
# git update-index --skip-worktree api-gateway/common/util/file_util.py
# git update-index --skip-worktree api-gateway/common/util/geo_util.py
# git update-index --skip-worktree api-gateway/common/util/str_util.py

# from django.contrib.gis.geos import GEOSGeometry, Polygon, MultiPolygon


# from django.conf import settings
# import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# from common.util.romsg import send as romsg_send

# import requests, urllib

# from django.contrib.gis.geos import Point

# SIDO_CODE_MAP = dict(
#     서울시='11',
#     부산시='26',
#     대구시='27',
#     인천시='28',
#     광주시='29',
#     대전시='30',
#     울산시='31',
#     세종시='36', # 세종시 좀 이상하긴 하지만 그냥 두자. 36110이고 36000은 없지만,,
#     경기도='41',
#     충청북도='43',
#     충청남도='44',
#     전라북도='45',
#     전라남도='46',
#     경상북도='47',
#     경상남도='48',
#     제주도='50',
#     강원도='51',
#     # 전라북도='52', # 여기도 무슨 특별자치도가 됨
# )

# CODE_SIDO_MAP = {
#     '11':'서울시',
#     '26':'부산시',
#     '27':'대구시',
#     '28':'인천시',
#     '29':'광주시',
#     '30':'대전시',
#     '31':'울산시',
#     '36':'세종시',
#     '41':'경기도',
#     '43':'충청북도',
#     '44':'충청남도',
#     '45':'전라북도',
#     '46':'전라남도',
#     '47':'경상북도',
#     '48':'경상남도',
#     '50':'제주도',
#     '51':'강원도',
#     '52':'전라북도', # 특별자치도가 된 듯
# }

# def fix_sido(juso):
#     juso = juso.strip()

#     if juso is None:
#         return None

#     if juso == '':
#         return None

#     juso = juso.replace('서울특별시', '서울시')
#     juso = juso.replace('인천광역시', '인천시')
#     juso = juso.replace('부산광역시', '부산시')
#     juso = juso.replace('대구광역시', '대구시')
#     juso = juso.replace('대전광역시', '대전시')
#     juso = juso.replace('울산광역시', '울산시')
#     juso = juso.replace('광주광역시', '광주시')
#     juso = juso.replace('세종특별자치시', '세종시')
#     juso = juso.replace('세종 세종시', '세종시')
#     juso = juso.replace('강원특별자치도', '강원도')
#     juso = juso.replace('제주특별자치도', '제주도')
#     juso = juso.replace('전북특별자치도', '전라북도')

#     try:
#         splitted = juso.split()
#         sido = splitted[0]
#         if sido == '서울':
#             return ' '.join(['서울시'] + splitted[1:])

#         if sido == '부산':
#             return ' '.join(['부산시'] + splitted[1:])

#         if sido == '대구':
#             return ' '.join(['대구시'] + splitted[1:])

#         if sido == '인천':
#             return ' '.join(['인천시'] + splitted[1:])

#         if sido == '광주':
#             return ' '.join(['광주시'] + splitted[1:])

#         if sido == '대전':
#             return ' '.join(['대전시'] + splitted[1:])

#         if sido == '울산':
#             return ' '.join(['울산시'] + splitted[1:])

#         if sido == '세종':
#             return ' '.join(['세종시'] + splitted[1:])

#         if sido == '경기':
#             return ' '.join(['경기도'] + splitted[1:])

#         if sido == '충북':
#             return ' '.join(['충청북도'] + splitted[1:])

#         if sido == '충남':
#             return ' '.join(['충청남도'] + splitted[1:])

#         if sido == '전북':
#             return ' '.join(['전라북도'] + splitted[1:])

#         if sido == '전남':
#             return ' '.join(['전라남도'] + splitted[1:])

#         if sido == '경북':
#             return ' '.join(['경상북도'] + splitted[1:])

#         if sido == '경남':
#             return ' '.join(['경상남도'] + splitted[1:])

#         if sido == '제주':
#             return ' '.join(['제주도'] + splitted[1:])

#         if sido == '강원':
#             return ' '.join(['강원도'] + splitted[1:])

#         return juso
#     except Exception as e:
#         print(e)
#         print(f'juso _{juso}_')
#         raise e

# def get_jj_by_pnu(pnu):
#     # https://www.vworld.kr/dev/v4dv_2ddataguide2_s003.do?svcIde=cadastral
#     # pnu 체크시
#     # http://localhost:2311/adminachy/roregion/bjd/?q=41194104

#     pnu = fix_pnu(pnu)

#     url = f'http://localhost:4105/api/jijeokcore/core/{pnu}/'
#     # print(url)
#     resp = requests.request(
#         method= 'get',
#         url= url,
#         timeout= 20 # seconds / 밀리세컨 아님
#     )

#     # 정부데이터는 지목이 없음. 지목은 따로 가져와야 할 듯. 아니면 토지특성에서 가져오든지

#     datum = resp.json()

#     if 'detail' in datum.keys() and datum['detail'] == 'Not found.':
#         return None

#     bjd = bjd_from_code(datum['properties']['bjd_cd'])
#     jibun = datum['properties']['jibun']
#     if datum['id'][10] == '2':
#         jibun = f'산 {jibun}'

#     datum['properties']['addr'] = f"{bjd} {jibun}"
#     datum['properties']['jimok'] = fix_jimok(datum['properties']['jimok'])

#     return datum

# def get_jj_by_pnu_from_gov(pnu):

#     gov_url= f'https://api.vworld.kr/req/data?service=data&version=2.0&request=GetFeature&key={settings.VWORLD_KEY}&format=json&errorformat=json&size=10&page=1&data=LP_PA_CBND_BUBUN&attrfilter=pnu:=:{pnu}&columns=pnu,jibun,bonbun,bubun,ag_geom,addr,gosi_year,gosi_month,jiga&geometry=true&attribute=true&crs=EPSG:900913&domain=https://tojimetric.com'

#     resp = requests.request(
#         method= 'get',
#         url= gov_url,
#         timeout= 20 # seconds / 밀리세컨 아님
#     )
#     json_obj = resp.json()['response']

#     if json_obj['status'] != 'OK':
#         # pp.pprint(json_obj)
#         return None

#     datum = json_obj['result']['featureCollection']['features'][0]

#     return datum

# def get_jj_by_pnu_disco(pnu):
#     # x, y는 그냥 아무거나
#     url = f'https://polygon.disco.re/get_arch_road/?pnu={pnu}&x=126.987567326919&y=37.5398593298984&spec=goon'
#     resp = requests.request(
#         method= 'get',
#         url= url,
#         timeout= 20 # seconds / 밀리세컨 아님
#     )
#     if resp.status_code == 400:
#         pp.pprint(resp.json())
#         return 'N/A'

#     if resp.status_code == 500:
#         raise Exception('500 error')

#     if not resp.text:
#         raise Exception('no response')

#     datum = resp.json()

#     # 에러 체크 넣을 것

# # { 'polygon': [ { 'click': '1',
# #                  'dong': '',
# #                  'dong1': None,
# #                  'type': '1',
# #                  'value': 'POLYGON ((126.866622714615 '
# #                           '37.2366697843491,126.866640194201 '
# #                           '37.2367750056217,126.866767726663 '
# #                           '37.2367616244728,126.866748105401 '
# #                           '37.2366565720075,126.866622714615 '
# #                           '37.2366697843491))'}]}

#     if len(datum['polygon']) == 0: return None

#     ret = {}
#     polygon_str = datum['polygon'][0]['value']
#     geom = MultiPolygon(GEOSGeometry(polygon_str))
#     # print(geom)
#     # ret['geom'] = MultiPolygon([Polygon(datum['polygon'][0]['value'])])
#     ret['pnu'] = pnu
#     ret['geom'] = geom

#     return ret

# def get_jj_by_xy_naver(x, y):
#     url = f'https://map.naver.com/p/api/polygon?lat={y}&lng={x}&order=jibun'
#     resp = requests.request(
#         method= 'get',
#         url= url,
#         timeout= 20 # seconds / 밀리세컨 아님
#     )

#     if resp.status_code == 400:
#         pp.pprint(resp.json())
#         return 'N/A'

#     if resp.status_code == 500:
#         raise Exception('500 error')

#     if not resp.text:
#         raise Exception('no response')

#     datum = resp.json()

#     ret = {}
#     if 'features' in datum.keys() and len(datum['features']) > 0:
#         ret = datum['features'][0]
#     else:
#         return None

#     ret['properties']['addr'] = get_juso_by_pnu(ret['properties']['pnucode'])
#     ret['geometry']['coordinates'] = [ret['geometry']['coordinates']]
#     ret['geometry']['type'] = 'MultiPolygon'

#     # pp.pprint(ret['geometry']['coordinates'])
#     try:
#         ret['geom'] = MultiPolygon([Polygon(ret['geometry']['coordinates'][0][0])])
#     except Exception as e:
#         print(str(e) == 'Dimension mismatch.')
#         print('get_jj_by_xy_naver')
#         # pp.pprint(ret)
#         raise e

#     ret['pnu'] = ret['properties']['pnucode']

#     return ret

# def get_jj_by_xy(x, y):
#     url = f'http://localhost:4112/api/jijeokcore/core-by-xy/{x}/{y}/'
#     resp = requests.request(
#         method= 'get',
#         url= url,
#         timeout= 20 # seconds / 밀리세컨 아님
#     )

#     if resp.status_code == 400:
#         # pp.pprint(resp.json())
#         return 'N/A'

#     if resp.status_code == 500:
#         raise Exception('500 error')

#     if not resp.text:
#         raise Exception('no response')

#     datum = resp.json()

#     # pp.pprint(datum)

#     datum['properties']['addr'] = datum['properties']['jibun_juso']
#     datum['pnu'] = datum['properties']['code']
#     datum['geom'] = MultiPolygon([Polygon(datum['geometry']['coordinates'][0][0])])

#     return datum

# def get_kakao_place(keyword, x=None, y=None, context=None):
#     # print('get_kakao_place keyword', keyword)
#     url = f'https://dapi.kakao.com/v2/local/search/keyword.json'
#     params = {
#         'query': keyword,
#     }
#     if x and y:
#         params['x'] = x
#         params['y'] = y

#     response = requests.request(
#         method= 'get',
#         url= url,
#         params= params,
#         headers= {
#             # "Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"
#             "Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"
#         },
#         timeout= 5 # seconds / 밀리세컨 아님
#     )
#     pp.pprint(response.json())

# def _call_kakao_juso(juso):
#     url = f'https://dapi.kakao.com/v2/local/search/address.json?page=1&size=5&query={juso}'
#     # print(url)
#     # url = f'curl -X GET "https://dapi.kakao.com/v2/local/search/address.json?page=1&size=5&query={self.target.addr}" -H "Authorization: KakaoAK {settings.KAKAO_REST_API_KEY}"'
#     # 5a70a126bb26b45dbbd7829fb374e09f
#     response = requests.request(
#         method= 'get',
#         url= url,
#         params= {},
#         headers= {
#             # "Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"
#             "Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"
#         },
#         timeout= 5 # seconds / 밀리세컨 아님
#     )

#     # print(response.text)
#     return json.loads(response.text)

# def _reduce_boo(juso):
#     last = int(juso[-1])
#     if last > 1:
#         juso = juso[:-1] + str(last - 1)
#     if last == 1:
#         juso = juso[:-2]
#     return juso


# def get_kakao_juso(juso, context=None):
#     # print('get_kakao_juso juso: ', juso)
#     if juso == '':
#         return {}, False

#     romsg_text = ''
#     if context and context['meta']:
#         romsg_text = '[' + context['meta'] + '] '

#     is_similar_geom = False
#     resp = _call_kakao_juso(juso)
#     if len(resp['documents']) == 0 and juso[-1].isnumeric():
#         is_similar_geom = True
#         juso = _reduce_boo(juso)
#         resp = _call_kakao_juso(juso)
#         if len(resp['documents']) == 0 and juso[-1].isnumeric():
#             juso = _reduce_boo(juso)
#             resp = _call_kakao_juso(juso)
#             if len(resp['documents']) == 0 and juso[-1].isnumeric():
#                 juso = _reduce_boo(juso)
#                 resp = _call_kakao_juso(juso)
#                 if len(resp['documents']) == 0:
#                     return resp, False

#     if len(resp['documents']) == 0:
#         return resp, False

#     doc_obj = resp['documents']
#     ret = {}

#     doc = doc_obj[0]

#     ret['주소_input'] = juso
#     addr = doc.get('address', None)
#     if not addr:
#         romsg_text += '지번주소가 없습니다: ' + juso
#         romsg_send(romsg_text)
#         return {}, False

#     ret['지번주소'] = doc['address']['address_name']
#     ret['도로명주소'] = None
#     ret['zone_no'] = None
#     ret['지하'] = None
#     if doc['road_address']:
#         ret['도로명주소'] = doc['road_address']['address_name']
#         ret['zone_no'] = doc['road_address']['zone_no']
#         ret['지하'] = doc['road_address']['underground_yn'] == 'Y'

#     ret['시도'] = doc['address']['region_1depth_name']
#     ret['시군구'] = doc['address']['region_2depth_name']
#     ret['읍면동'] = doc['address']['region_3depth_name']
#     ret['읍면동_행정'] = doc['address']['region_3depth_h_name']
#     if ret['읍면동'] == '' and ret['읍면동_행정'] != '':
#         ret['읍면동'] = ret['읍면동_행정']

#     ret['산'] = doc['address']['mountain_yn'] == 'Y'
#     ret['본번'] = doc['address']['main_address_no']
#     ret['부번'] = doc['address']['sub_address_no']

#     san = '1'
#     if ret['산']:
#         san = '2'
#     ret['pnu'] = doc['address']['b_code'] + san + ret['본번'].zfill(4) + ret['부번'].zfill(4)

#     ret['point'] = Point(x= float(doc['x']), y= float(doc['y']))
#     ret['center'] = ret['point']
#     ret['is_similar_geom'] = is_similar_geom
#     return ret, True

# def juso_from_code(pnu):
#     got = get_juso_by_pnu(pnu)
#     if got:
#         return got.strip()
#     return None

# def get_juso_by_pnu(pnu):
#     pnu = fix_pnu(pnu)
#     got = bjd_from_code(pnu)
#     # pp.pprint(got)

#     bon = pnu[11:15].lstrip('0')
#     bu = pnu[15:19].lstrip('0')
#     if bu != '0000':
#         jibun = f'{bon}-{bu}'
#     else:
#         jibun = bon

#     if len(pnu) > 10 and pnu[10] == '2':
#         jibun = f'산 {jibun}'

#     if not got:
#         return None

#     if jibun[-1] == '-':
#         jibun = jibun[:-1]

#     return got + ' ' + jibun

# def get_tojits_by_pnu(pnu):
#     pnu = fix_pnu(pnu)
#     url = f'http://localhost:4105/api/tojits/{pnu}/'
#     # print(url)
#     resp = requests.request(
#         method= 'get',
#         url= url,
#         timeout= 20 # seconds / 밀리세컨 아님
#     )
#     datum = resp.json()

#     if 'detail' in datum.keys() and datum['detail'] == 'Not found.':
#         return None

#     return datum

# def get_tojits(params):
#     url = f'http://localhost:4105/api/tojits/tojits/'
#     # print(url)
#     resp = requests.request(
#         method= 'get',
#         url= url,
#         params= params,
#         timeout= 20 # seconds / 밀리세컨 아님
#     )
#     return resp.json()

# def is_sido_supported(code):
#     try:
#         get_sido(code)
#     except:
#         return False
#     return True

# def get_short_sido(sido):
#     sido = sido.replace('서울특별시', '서울시')
#     sido = sido.replace('인천광역시', '인천시')
#     sido = sido.replace('부산광역시', '부산시')
#     sido = sido.replace('대구광역시', '대구시')
#     sido = sido.replace('대전광역시', '대전시')
#     sido = sido.replace('울산광역시', '울산시')
#     sido = sido.replace('광주광역시', '광주시')
#     sido = sido.replace('세종특별자치시', '세종시')
#     sido = sido.replace('강원특별자치도', '강원도')
#     return sido

# def get_pnu(juso):
#     # 로컬 주소 ms
#     url = f'http://localhost:1211/api/search/?q={juso}'
#     # print(url)
#     resp = requests.request(
#         method= 'get',
#         url= url,
#         # params= params,
#         timeout= 20 # seconds / 밀리세컨 아님
#     )

#     if resp.status_code == 400:
#         print(resp.text)
#         return 'N/A'

#     if resp.status_code == 500:
#         raise Exception('500 error')

#     if not resp.text:
#         raise Exception('no response')

#     datum = resp.json()
#     # pp.pprint(datum)

#     for _pnu, searched_juso in datum['results']:
#         searched_juso = get_short_sido(searched_juso)
#         if juso == searched_juso:
#             return _pnu[1:]

#     return None

# def get_pnu_from_code(juso):
#     is_san = False
#     juso_spl = juso.split()

#     juso_wo_bunji = ''
#     if '산' in juso_spl[-1]:
#         is_san = True

#     san_code = '1'
#     if is_san:
#         san_code = '2'

#     if not juso_spl[-1].replace('산', '').isnumeric():
#         raise Exception('not implemented')

#     juso_wo_bunji = ' '.join(juso_spl[:-1])
#     # reverse key, value
#     REV_REG_CODE = {}
#     for k, v in settings.REG_CODE.items():
#         REV_REG_CODE[v] = k

#     bjd_cd = REV_REG_CODE[juso_wo_bunji]
#     print('juso_wo_bunji', juso_wo_bunji, bjd_cd)

#     bunji = juso_spl[-1]

#     bunji_spl = bunji.split('-')
#     if len(bunji_spl) == 1:
#         return bjd_cd + san_code + bunji_spl[0].zfill(4) + '0000'

#     raise Exception('not implemented')

# def sido_from_code(code):
#     sido_cd = code[:2]
#     return CODE_SIDO_MAP[sido_cd]

# # def sgg_from_code(code):
# #     import sgg.models as sgg_models
# #     # print('sgg_from_code', code)
# #     got = sgg_models.Sgg.objects.filter(sgg_cd=code[:5]).first()
# #     if not got:
# #         return None, None
# #     return got.sgg, got

# def sgg_from_code(code):

#     sido_nm = sido_from_code(code)
#     sgg_nm = fix_sido(settings.REG_CODE[code[:5] + '00000'])

#     ret = {
#         'sgg_cd': code[:5],
#         'sgg_nm': sgg_nm,
#         'sgg_nm_only': sgg_nm_only(sido_nm, sgg_nm),
#     }

#     if ret['sgg_cd'][2:] == '000':
#         ret['sgg_cd'] = None
#         ret['sgg_nm'] = None
#         ret['sgg_nm_only'] = None

#     return ret

# def bjd_from_code(code):
#     bjd_cd = code[:10]
#     if len(bjd_cd) != 10:
#         bjd_cd = code[:8] + '00'
#     # print('bjd_cd', bjd_cd, bjd_cd[6:], bjd_cd[5:])
#     if bjd_cd[5:] == '00000':
#         return None

#     bjd = settings.REG_CODE.get(bjd_cd)
#     if bjd is None:
#         # 강원특별자치도로 바뀌고 나서도 제대로 반영이 안된 경우가 있음
#         if bjd_cd[:2] == '51':
#             bjd = settings.REG_CODE.get('42' + bjd_cd[2:])
#     if bjd is None:
#         # 강원특별자치도로 바뀌고 나서도 제대로 반영이 안된 경우가 있음
#         if bjd_cd[:2] == '42':
#             bjd = settings.REG_CODE.get('51' + bjd_cd[2:])
#     if bjd is None:
#         return None
#     return fix_sido(bjd)

# def remove_li(bjd_nm):
#     if bjd_nm is None:
#         return None
#     splitted = bjd_nm.split()
#     last = splitted[-1]
#     if last[-1] == '리':
#         return ' '.join(splitted[:-1])

#     return bjd_nm

# def sgg_nm_only(sido_nm, sgg_nm):
#     if sgg_nm == '세종시': return sgg_nm
#     if sgg_nm is None: return None
#     return sgg_nm.replace(sido_nm, '').strip()

# def bjd_nm_only(bjd_nm):
#     if bjd_nm is None:
#         return None
#     splitted = bjd_nm.split()
#     last = splitted[-1]
#     if last[-1] == '리':
#         return splitted[-2]

#     if last[-1] in ['읍', '면', '동', '가', '로']:
#         return splitted[-1]

#     if last[-1] == ')':
#         # 4311425350  충청북도 청주시 청원구 오창읍 화산리(花山) 이런 게 있음
#         return splitted[-1].split('(')[0]

#     raise Exception(f'unknown bjd_nm: {bjd_nm}')

# def fix_bjd_nm(bjd_nm):
#     # print('fix_bjd_nm', bjd_nm)
#     if '고양시일산서구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('고양시일산서구', '고양시 일산서구')
#     if '고양시일산동구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('고양시일산동구', '고양시 일산동구')
#     if '고양시덕양구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('고양시덕양구', '고양시 덕양구')

#     if '용인시처인구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('용인시처인구', '용인시 처인구')
#     if '용인시기흥구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('용인시기흥구', '용인시 기흥구')
#     if '용인시수지구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('용인시수지구', '용인시 수지구')

#     if '성남시중원구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('성남시중원구', '성남시 중원구')
#     if '성남시수정구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('성남시수정구', '성남시 수정구')
#     if '성남시분당구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('성남시분당구', '성남시 분당구')

#     if '안산시단원구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('안산시단원구', '안산시 단원구')
#     if '안산시상록구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('안산시상록구', '안산시 상록구')

#     if '수원시팔달구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('수원시팔달구', '수원시 팔달구')
#     if '수원시장안구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('수원시장안구', '수원시 장안구')
#     if '수원시권선구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('수원시권선구', '수원시 권선구')
#     if '수원시영통구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('수원시영통구', '수원시 영통구')

#     if '안양시동안구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('안양시동안구', '안양시 동안구')
#     if '안양시만안구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('안양시만안구', '안양시 만안구')

#     if '부천시소사구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('부천시소사구', '부천시 소사구')
#     if '부천시원미구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('부천시원미구', '부천시 원미구')
#     if '부천시오정구' in bjd_nm:
#         bjd_nm = bjd_nm.replace('부천시오정구', '부천시 오정구')

#     return bjd_nm

# def jibun_from_code(code):
#     bon = code[11:15].lstrip('0')
#     bu = code[15:19].lstrip('0')
#     if bu != '0000':
#         ret = f'{bon}-{bu}'
#         if ret[-1] == '-':
#             return ret[:-1]
#         return ret
#     return bon

# def juso_dict_from_pnu(pnu):
#     if pnu is None: return {}

#     juso_dict = _juso_dict_from_pnu(pnu)

#     # change '' to None
#     for k, v in juso_dict.items():
#         if v == '':
#             juso_dict[k] = None

#     return juso_dict

# def _juso_dict_from_pnu(pnu):

#     # 정부데이터에는 법정동에 리가 붙어있음
#     sido_nm = sido_from_code(pnu)

#     ret = {
#         'sido_cd': pnu[:2],
#         'sido_nm': sido_nm,
#     }

#     sgg_dict = sgg_from_code(pnu)

#     ret = {**ret, **sgg_dict}

#     bjd_nm = bjd_from_code(pnu)
#     jibun = jibun_from_code(pnu)

#     if bjd_nm is None: return ret

#     bjd_ret = {
#         'bjd_cd': pnu[:8],
#         'bjd_nm': remove_li(bjd_nm),
#         'bjd_nm_only': bjd_nm_only(bjd_nm),
#     }

#     ret = {**ret, **bjd_ret}

#     if len(pnu) == 10 and pnu[-2:] == '00':
#         # 법정동까지만
#         return ret

#     bjd = bjd_nm.strip()

#     if bjd[-1] == '리':
#         splitted = bjd.split()
#         ret['li_cd'] = pnu[:10]
#         ret['li_nm'] = bjd
#         ret['li_nm_only'] = splitted[-1]

#     if len(pnu) == 10 and pnu[-2:] != '00':
#         # 리까지만
#         return ret

#     # pnu가 아닌 것도 처리할 수 있도록 함
#     if len(pnu) > 9:
#         is_san = pnu[10] == '2'
#     else:
#         is_san = None

#     ret['is_san'] = is_san
#     ret['jibun'] = jibun
#     ret['jibun_juso'] = juso_from_code(pnu)

#     ret['last_two'] = ret['bjd_nm_only']
#     if ret.get('li_cd', None):
#         ret['last_two'] += ' ' + ret['li_nm_only']

#     if ret['is_san']:
#         ret['last_two'] += ' 산'
#     ret['last_two'] += ' ' + ret['jibun']

#     ret['last_two'] = ret['last_two'].strip()

#     return ret


# JIMOK_MAP = {
#     '공':'공원',
#     '과':'과수원',
#     '광':'광천지',
#     '구':'구거',
#     '답':'답',
#     '대':'대지',
#     '도':'도로',
#     '목':'목장용지',
#     '묘':'묘지',
#     '사':'사적지',
#     '수':'수도용지',
#     '양':'양어장',
#     '염':'염전',
#     '원':'유원지',
#     '유':'유지',
#     '임':'임야',
#     '잡':'잡종지',
#     '장':'공장용지',
#     '전':'전',
#     '제':'제방',
#     '종':'종교용지',
#     '주':'주유소용지',
#     '차':'주차장',
#     '창':'창고용지',
#     '천':'하천',
#     '철':'철도용지',
#     '체':'체육용지',
#     '학':'학교용지',
# }

# REVERSE_JIMOK_MAP = {v: k for k, v in JIMOK_MAP.items()}

# # FINAL_YONGDO_MAP = {
# #     '주거용': ['아파트', '다세대/빌라', '주택', '근린주택', '다가구주택'],
# #     '상업용': ['근린상가', '근린시설', '오피스텔', '사무실', '교육시설', '노유자시설', '공장', , '아파트형공장', '창고', '자동차시설', '주유소', '농가시설', '숙박시설', '사우나시설', '의료시설', '종교시설', '문화/집회시설', '상업용기타'],
# #     '토지': JIMOK_MAP.keys() ++ JIMOK_MAP.values(),
# # }

# # def get_final_yongdo_category(text):
# #     text = ''.join(text.split())
# #     if text in REVERSE_JIMOK_MAP.keys():
# #         jimok = REVERSE_JIMOK_MAP[text]
# #         if jimok in FINAL_YONGDO_MAP['토지']:
# #             return '토지'
# #         if jimok in FINAL_YONGDO_MAP['주거용']:
# #             return '주거용'
# #         if jimok in FINAL_YONGDO_MAP['상업용']:
# #             return '상업용'
# #         return '기타'

# def fix_jimok(text, original=None):

#     if text == '':
#         return ''

#     if text is None:
#         return None

#     if text == '?' or text == '？': # 이상한 물음표 기호도 있음
#         return None

#     if text.strip() == 'a': # a는 대지였음
#         return None

#     if text.strip() == 'A': # 라?_?A
#         return None

#     if text.strip() == 'o': # o는 하천
#         return None

#     if text.strip() == '가': # 가 라는 건 또 뭐냐.. 찾아보면 전이긴 한데,,
#         return None

#     if text == '하': return '천'

#     if len(text) == 1:
#         if text in JIMOK_MAP.keys(): return text

#         # 지목이 없는 경우가 있음
#         if text.isnumeric():
#             return None

#         splitted = original.split()
#         if len(splitted) == 2 and splitted[1] in REVERSE_JIMOK_MAP.keys():
#             # print('REVERSE_JIMOK_MAP[splitted[1]]', REVERSE_JIMOK_MAP[splitted[1]])
#             return REVERSE_JIMOK_MAP[splitted[1]]

#         raise Exception(f'unknown jimok: {text} / original: {original}')

#     if text == '양어장용지': text = '양어장'
#     if text == '전답': text = '전'
#     if text == '주유소': text = '주유소용지'
#     return REVERSE_JIMOK_MAP[text]

# def fix_pnu(pnu):
#     # 전북이 45에서 52로 바뀜
#     pnu = pnu.strip()

#     if pnu is None or pnu == '':
#         raise Exception('pnu is None or empty')

#     if pnu[:2] == '45': return '52' + pnu[2:]
#     return pnu

# def code_from_sgg_nm(sgg_nm):
#     # print('-------- code_from_sgg_nm', sgg_nm)
#     import sgg.models as sgg_models
#     # print('sgg_from_code', code)
#     got = sgg_models.Sgg.objects.filter(sgg=sgg_nm).first()
#     if not got:
#         REVERSE_REG_CODE = {v: k for k, v in settings.REG_CODE.items()}
#         # print(REVERSE_REG_CODE)
#         got_code = REVERSE_REG_CODE.get(sgg_nm)
#         # print('------------------got_code', got_code)
#         if not got_code:
#             return None, None
#         else:
#             # make obj
#             splitted = sgg_nm.split()
#             sido_nm = splitted[0]
#             got = Namespace(**{
#                 'sido': sido_nm,
#                 'sido_cd': SIDO_CODE_MAP[sido_nm],
#                 'sgg': sgg_nm,
#                 'sgg_cd': got_code
#             })
#             return got_code, got
#     return got.sgg, got

# def get_tojits_by_pnu_from_gov(pnu):

#     gov_url=f'https://api.vworld.kr/ned/data/getLandCharacteristics?pnu={pnu}&format=json&key={settings.VWORLD_KEY}&numOfRows=1000&domain=https://tojimetric.com'

#     resp = requests.request(
#         method= 'get',
#         url= gov_url,
#         timeout= 20 # seconds / 밀리세컨 아님
#     )
#     try:
#         json_obj = resp.json()

#         if json_obj['response']['totalCount'] == '0':
#             return None

#         return json_obj
#     except Exception as e:
#         print(e)
#         print(resp.text)
#         return None

# def get_tojits_by_pnu_from_disco(pnu):

#     disco_url=f'https://data.disco.re/home/land_by_pnu/?pnu={pnu}'
#     resp = requests.request(
#         method= 'get',
#         url= disco_url,
#         timeout= 10 # seconds / 밀리세컨 아님
#     )
#     try:
#         json_obj = resp.json()
#         return json_obj
#     except Exception as e:
#         print(e)
#         print(resp.text)
#         return None

# def get_naver_juso(juso):
#     # 이건 많이 하면 짤림
#     # https://map.naver.com/p/api/search/allSearch?query=%EA%B2%BD%EA%B8%B0%EB%8F%84+%EC%88%98%EC%9B%90%EC%8B%9C+%EC%9E%A5%EC%95%88%EA%B5%AC+%EC%A1%B0%EC%9B%90%EB%8F%99+519-88&type=all&searchCoord=&boundary=

#     # curl
#     # curlreq.get("https://map.naver.com/p/api/search/allSearch?query=%EA%B2%BD%EA%B8%B0%EB%8F%84+%EC%88%98%EC%9B%90%EC%8B%9C+%EC%9E%A5%EC%95%88%EA%B5%AC+%EC%A1%B0%EC%9B%90%EB%8F%99+519-88&type=all&searchCoord=&boundary=")

#     # 하다보면 짤리는데 curlreq로 해도 안됨. request할 때 이것저것 넣어야 할듯. 근데 이걸 꼭 해야할지는 모르겠음. 해야 한다면 나중에 필요할 때 구현할 것.

#     juso = juso.replace(' ', '+')
#     url = f'https://map.naver.com/p/api/search/allSearch?query={juso}&type=all&searchCoord=&boundary='
#     response = requests.request(
#         method= 'get',
#         url= url,
#         params= {},
#         timeout= 5 # seconds / 밀리세컨 아님
#     )
#     # print(response)
#     if response.status_code != 200:
#         print(response.text)
#         return None

#     resp_json = json.loads(response.text)
#     result_list = resp_json['result']['address']['jibunsAddress']['list']
#     if len(result_list) == 0:
#         print('no result')
#         return None

#     result = result_list[0]
#     # pp.pprint(result)

#     return dict(
#         juso= result['koreanAddress'],
#         x= result['x'],
#         y= result['y'],
#     )
