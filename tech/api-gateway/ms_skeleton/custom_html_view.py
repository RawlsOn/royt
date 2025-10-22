from django.urls import re_path, path, include
from django.contrib import admin
import requests, urllib
from django.utils import timezone
import dateutil.relativedelta

import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

하한가_층수_기준 = 3

import main.models as main_models
import config.models as config_models

from django.template.response import TemplateResponse, HttpResponse

def judge_view(request, id):
    print('------------------', id)
    if not request.user.is_authenticated:
        return HttpResponse('UNAUTHORIZED')

    final = make_final_data(id)
    context = dict(
        admin.site.each_context(request),
        data= final,
    )
    return TemplateResponse(request, "admin/judge.html", context)

def make_final_data(id):
    user_apply = main_models.UserApply.objects.get(id= id)

    final = {}

    apart = json.loads(user_apply.apart_json_str)

    final['신청인'] = user_apply.user_name
    final['연락처'] = user_apply.user_phone
    final['물건주소'] = user_apply.road_juso + ' (' + apart['kb_danji_name'] + ')'
    final['선순위대출액'] = format(user_apply.pre_loan_amount * 10000, ',d') + '원'

    final['동'] = user_apply.apart_dong
    final['호'] = user_apply.apart_ho


    found = list(filter(lambda x: x['title'] == user_apply.selected_type, apart['apartmentS_area_types']))[0]

    final['공급면적'] = str(found['gong_geup_area_pyeong']) + '평'
    final['전용면적'] = str(found['jeon_yong_area_pyeong']) + '평'

    final['총세대수'] = apart['kb_chong_sedae_count']

    url = os.getenv('KB_SISE_MS_URL') + '/sise'
    response = requests.request(
        method= 'get',
        url= url,
        params= {'danji_id': found['kb_danji_id'], 'area_id': found['kb_area_id']},
        timeout= 5 # seconds / 밀리세컨 아님
    )
    # print(json.loads(response.text))

    sise = json.loads(response.text)['results'][-1]
    # pp.pprint(sise)

    final['KB시세_상한가'] = format(sise['maemae_top_price'] * 10000, ',d') + '원'
    final['KB시세_일반가'] = format(sise['maemae_ilban_trans_price'] * 10000, ',d') + '원'
    final['KB시세_하한가'] = format(sise['maemae_bottom_price'] * 10000, ',d') + '원'

    ho_int = 0
    if len(final['호']) == 1:
        ho_int = int(final['호'])
    else:
        ho_int = int(final['호'][:-2])

    if ho_int <= 하한가_층수_기준:
        applied_price = sise['maemae_bottom_price'] * 10000
    else:
        applied_price = sise['maemae_ilban_trans_price'] * 10000

    final['적용시세'] = format(applied_price, ',d') + '원'

    final['KB_링크'] = 'https://kbland.kr/c/' + str(found['kb_danji_id'])

    url = 'https://history-sise-ms-ec2.vfintech.co.kr/api/sise'
    print('url', url)
    response = requests.request(
        method= 'get',
        url= url,
        params= {'danji_id': found['kb_danji_id'], 'area_id': found['kb_area_id']},
        timeout= 5 # seconds / 밀리세컨 아님
    )

    # print('response.text', response.text)
    history_sise = json.loads(response.text)['results']

    매매실거래_list = list(filter(lambda x: x['매매실거래거래량'], history_sise))
    매매실거래_list_sorted = list(sorted(매매실거래_list, key=lambda d: d['기준년월'], reverse= True))

    매매실거래_final_list = []
    for datum in 매매실거래_list_sorted:
        ret_datum = {}
        ret_datum['기준년월'] = datum['기준년월']
        ret_datum['기준년월_han'] = datum['기준년월'][:4] + '년 ' + datum['기준년월'][4:] + '월'
        if datum['매매실거래거래량'] > 1:
            for price in datum['매매실거래금액s'].split('|'):
                ret_datum['매매실거래금액_han'] = format(int(price) * 10000, ',d') + '원'
                ret_datum['매매실거래금액'] = int(price) * 10000
                매매실거래_final_list.append(ret_datum)
        else:
            ret_datum['매매실거래금액_han'] = format(int(datum['매매실거래금액s']) * 10000, ',d') + '원'
            ret_datum['매매실거래금액'] = int(datum['매매실거래금액s']) * 10000
            매매실거래_final_list.append(ret_datum)

    # pp.pprint(매매실거래_final_list)
    # print(len(매매실거래_final_list))

    final['total_실거래가_list_text'] = json.dumps(매매실거래_final_list, ensure_ascii=False, indent=4)
    final['실거래가_list'] = 매매실거래_final_list[:5]
    final['실거래가_count'] = len(final['실거래가_list'])
    final['실거래가_rowspan'] = final['실거래가_count'] + 1
    # print("final['실거래가_count']", final['실거래가_count'])

    now = timezone.now()
    ago_1_month = (now + dateutil.relativedelta.relativedelta(months=-1)).strftime('%Y%m')
    ago_6_month = (now + dateutil.relativedelta.relativedelta(months=-6)).strftime('%Y%m')
    ago_12_month = (now + dateutil.relativedelta.relativedelta(months=-12)).strftime('%Y%m')
    ago_24_month = (now + dateutil.relativedelta.relativedelta(months=-24)).strftime('%Y%m')
    # print('ago_1_month', ago_1_month)
    # print('ago_6_month', ago_6_month)
    # print('ago_12_month', ago_12_month)
    # print('ago_24_month', ago_24_month)

    final['평균실거래가'] = {
        '최근_01개월': {},
        '최근_06개월': {},
        '최근_12개월': {},
        '최근_24개월': {}
    }

    final['평균실거래가']['최근_01개월'] = make_실거래가(ago_1_month, 매매실거래_final_list)
    final['평균실거래가']['최근_06개월'] = make_실거래가(ago_6_month, 매매실거래_final_list)
    final['평균실거래가']['최근_12개월'] = make_실거래가(ago_12_month, 매매실거래_final_list)
    final['평균실거래가']['최근_24개월'] = make_실거래가(ago_24_month, 매매실거래_final_list)

    # pp.pprint(apart)

    sigungu_code = apart['kb_bjd_code'][:5] + '00000'
    sido_code = apart['kb_bjd_code'][:2] + '00000000'

    # 시군구 코드로 먼저 찾음
    found_coef = config_models.Coef.objects.filter(code= sigungu_code).last()
    if not found_coef:
        found_coef = config_models.Coef.objects.filter(code= sido_code).last()


    final['prediction'] = pred = {}
    pred['coef'] = found_coef.to_obj

    pred['평균가격_num'] = applied_price * found_coef.평균값
    pred['평균가격'] = format(int(pred['평균가격_num']), ',d') + '원'

    pred['fore_1_month_min_num'] = applied_price * found_coef.conf_int5
    pred['fore_1_month_min'] = format(int(pred['fore_1_month_min_num']), ',d') + '원'

    pred['fore_1_month_man_num'] = applied_price * found_coef.conf_int95
    pred['fore_1_month_max'] = format(int(pred['fore_1_month_man_num']), ',d') + '원'

    pred['fore_4_month_min_num'] = applied_price - applied_price * found_coef.pred_int_3M
    pred['fore_4_month_min'] = format(int(pred['fore_4_month_min_num']), ',d') + '원'

    pred['fore_4_month_max_num'] = applied_price + applied_price * found_coef.pred_int_3M
    pred['fore_4_month_max'] = format(int(pred['fore_4_month_max_num']), ',d') + '원'

    return final

def make_실거래가(gijun_date, 매매실거래_final_list):
    ret = {'raw': [], 'avg': 'N/A', 'count': 0}
    ret['raw'] = list(filter(lambda x: x['기준년월'] >= gijun_date, 매매실거래_final_list))
    ret['count'] = len(ret['raw'])
    if ret['count'] > 0:
        ret['avg'] = format(int(sum([x['매매실거래금액'] for x in ret['raw']]) / ret['count']), ',d') + '원'
    return ret