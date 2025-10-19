# 네이버에 요청시 python의 requests로 하면 봇이라고 걸리는데 curl은 안걸려서 curl로 돌리도록 매핑함

import subprocess

from common.util.romsg import rp
import io, time, os, glob, pprint, json, re, shutil, ntpath
from django.utils import timezone
import common.util.datetime_util as dt_util

pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

import rawarticle.models as rawarticle_models

def get(url, params= {}):
    # if 'rletTpCd' not in params:
    #     params['rletTpCd'] = "APT%3AOPST%3AVL%3AABYG%3AOBYG%3AJGC%3AJWJT%3ADDDGG%3ASGJT%3AHOJT%3AJGB%3AOR%3AGSW%3ASG%3ASMS%3AGJCG%3ASG%3AGM%3ATJ%3AAPTHGJ"
    # if 'tradTpCd' not in params:
    #     params['tradTpCd'] = 'A1%3AB1%3AB2%3AB3'
    # if 'z' not in params:
    #     params['z'] = '16'
    # if 'sort' not in params:
    #     params['sort'] = 'dates'
    # print(url)
    # print(params)

    final_url = url + '?'
    for k, v in params.items():
        final_url += k + '=' + str(v) + '&'
    final_url = final_url[:-1]

    result = subprocess.check_output([
        "curl",
        final_url
    ], encoding='utf-8')

    # print(result)
    return result, final_url
    # return json.loads(result)

def get_article(article_no):
    url = "https://m.land.naver.com/article/info/" + article_no + "?newMobile"
    rp(url)
    return subprocess.check_output([
        "curl",
        "https://m.land.naver.com/article/info/" + article_no + "?newMobile"
    ], encoding='utf-8'), url

def save_article(article_no):
    found = rawarticle_models.Article.objects.filter(
        article_id= article_no,
        created_date= timezone.now()
    )
    if not found:
        text, url = get_article(article_no)
        rawarticle_models.Article.objects.create(
            article_id= article_no,
            text= text,
            url= url
        )

def get_with_more(url, params, cluster, func):
    result = ''
    if cluster.done_url:
        result, done_url = get(cluster.done_url)
    else:
        result, done_url = get(url, params)
    if result.strip() == '':
        rp('임시적으로 서비스 이용이 제한(막힌듯)', msg_type= 'IMPORTANT_NOTICE')
        raise ValueError('result is empty')
    if '임시적으로 서비스 이용이 제한' in result:
        rp('임시적으로 서비스 이용이 제한', msg_type= 'IMPORTANT_NOTICE')
        raise ValueError('result is empty')
    try:
        result_obj = json.loads(result)
        cluster.done_url = done_url
        cluster.save()
        func(result_obj, cluster)
        while result_obj['more']:
            next_page = result_obj['page'] + 1
            rp(cluster.sido + ' ' + cluster.sgg + ' ' + cluster.emd + ' ' + cluster.lgeo + ' more page exists: ' + ' ' + str(next_page))
            params['page'] = next_page
            result, done_url = get(url, params)
            if result.strip() == '':
                raise ValueError('result is empty')
            if '임시적으로 서비스 이용이 제한' in result:
                rp('임시적으로 서비스 이용이 제한', msg_type= 'NOTICE')
                raise ValueError('result is empty')
            cluster.done_url = done_url
            cluster.save()
            result_obj = json.loads(result)
            func(result_obj, cluster)
            dt_util.sleep_random()
    except Exception as e:
        # print('result----------', result)
        raise e

