# edit at 2024-05-16
# cp /Users/kimmyounghoon/Works/mkay/common/api-gateway/common/util/* ./api-gateway/common/util/

from django.conf import settings
import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# 용도지역지구_표준분류(2011.10.12).pdf 및 토지종합정보도면데이터베이스구축지침.pdf 참고

# 최신 : https://www.code.go.kr/stdcode/normalCodeL.do
# 여기서 도시정책/용도지역지구구분 다운로드

# 용도지역지구구분코드 조회자료.xls
# 여기 없으면 토지종합정보도면데이터베이스구축지침.pdf

CODEMAP = {}
with open(f'/usr/data/rostateplan{settings.RUNNING_ENV}/gov/docs/code-240219.csv', mode='r') as infile:
    reader = csv.reader(infile)
    CODEMAP = {rows[1]:rows[2] for rows in reader}

JUJEMAP = {}
with open(f'/usr/data/rostateplan{settings.RUNNING_ENV}/gov/docs/code-240219.csv', mode='r') as infile:
    reader = csv.reader(infile)
    JUJEMAP = {rows[1][:3]:rows[0] for rows in reader}

OLD_CODEMAP = {}
with open(f'/usr/data/rostateplan{settings.RUNNING_ENV}/gov/docs/code-old.csv', mode='r') as infile:
    reader = csv.reader(infile)
    OLD_CODEMAP = {rows[0]:rows[1] for rows in reader}

# pp.pprint(JUJEMAP)

def get_gubun(original_code, 주제도면):
    # print(f'original_code {original_code}, length:{len(original_code)}')
    if len(original_code) == 33:
        # print(code)
        code = original_code[20:26]
    elif len(original_code) == 26 or len(original_code) == 27 or len(original_code) == 28:
        # if original_code[16:18] == '경기':
        #     # 3990000413602012경기UFE1000001005 이런 게 있음
        #     code = original_code[18:]
        code = original_code[20:26]
        # check last character is alphabet
        if not code[2].isalpha():
            code = original_code[19:25]
        # print('code', code)
    elif len(original_code) == 30 or len(original_code) == 31 or len(original_code) == 32:
        code = original_code[20:26]
    elif len(original_code) == 9:
        if 주제도면 == '산림자원/산림자원조성관리':
            code = 'UFQ000'
    else:
        raise Exception(f'code length is not 33: {original_code} {len(original_code)}')
    # print('get_gubun', code)
    # pp.pprint(CODEMAP)

    depth1 = None
    depth2 = None
    depth3 = None

    # print("code[:4]", code[:4])
    depth1 = CODEMAP.get(code[:4] + '00', None)

    # print('depth1', depth1)
    if depth1 is None:
        depth1 = OLD_CODEMAP.get(code[:4] + '00', None)
        juje = JUJEMAP.get(code[:3], None)

    if code[5:6] != '00':
        depth2 = CODEMAP.get(code[:5] + '0', None)

        if code[5] != '0':
            depth3 = CODEMAP.get(code, None)

    juje = JUJEMAP.get(code[:3], None)
    if juje is None:
        if 'UFE100' in original_code:
            code = 'UFE100'
            juje = JUJEMAP.get(code[:3], None)
        elif 'UFN500' in original_code:
            code = 'UFN500'
            juje = JUJEMAP.get(code[:3], None)
        else:
            raise Exception(f'juje is None: {original_code} {code} {code[:3]} {len(original_code)}')

    if code[3:6] == '999':
        depth1 = depth3

    if depth1 is None:
        depth1 = CODEMAP.get(code[:3] + '000', None)

    if depth1 is None:
        raise Exception(f'depth1 is None: {original_code} {code} {len(original_code)}')

    ret = dict(
        depth1= depth1,
        depth2= depth2,
        depth3= depth3,
        juje= juje,
        main_code= code
    )
    return ret
