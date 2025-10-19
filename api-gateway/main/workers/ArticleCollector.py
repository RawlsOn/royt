from django.conf import settings

from common.util.romsg import rp as romsg_rp
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv, random
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models import QuerySet

import common.util.datetime_util as dt_util
import common.util.str_util as str_util
from common.util.logger import RoLogger
logger = RoLogger()
from argparse import Namespace
from common.util import curlreq
import rawarticle.models as rawarticle_models
import config.models as config_models
from main.workers.InstanceWatcher import InstanceWatcher
from common.util.AwsUtil import AwsUtil
from main.workers.ArticleDetailCollector import ArticleDetailCollector

# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# ./manage.py run_article_collector
# /home/admin/Works/mkay/onenlc/api-gateway/venv/bin/python /home/admin/Works/mkay/onenlc/api-gateway/manage.py run_article_collector
# ssh -i ~/.ssh/aws-ro-seoul.pem -o ServerAliveINterval=10 ec2-user@3.39.230.17


def rp(text, msg_type='INFO', filename='romsg', raise_error=False):
    romsg_rp(
        text,
        msg_type,
        filename='romsg_article_collector',
        raise_error= raise_error
    )

# https://m.land.naver.com/cluster/ajax/articleList?itemId=21233033&mapKey=&lgeo=21233033&rletTpCd=APT%3AOPST%3AVL%3AABYG%3AOBYG%3AJGC%3AJWJT%3ADDDGG%3ASGJT%3AHOJT%3AJGB%3AOR%3AGSW%3ASG%3ASMS%3AGJCG%3ASG%3AGM%3ATJ%3AAPTHGJ&tradTpCd=A1%3AB1%3AB2%3AB3&z=12

class ArticleCollector(object):

    def __init__(self, args={}):
        self.args = args
        self.aws_util = AwsUtil()

    def run(self):
        self.detail_collector = ArticleDetailCollector(Namespace(**{}))
        rp('Starting ArticleCollector')
        # rp('Check server ip :' + settings.SERVER_IP.strip(), msg_type='NOTICE')
        # found = rawarticle_models.BlockedIp.objects.filter(ip= settings.SERVER_IP.strip()).first()
        # if found:
        #     rp(settings.SERVER_IP + ': This server is blocked. Exiting...', msg_type='IMPORTANT_NOTICE')
        #     watcher.terminate_instance(found.instance_id)
        #     return

        working_seconds = int(dt_util.get_random_number(
            from_no= 60 * settings.MIN_COLLECTING_TIME_IN_MIN,
            to_no=   60 * settings.MAX_COLLECTING_TIME_IN_MIN,
        ))

        while True:

            elapsed_time = 0
            start_time = time.time()

            q = Q()
            # https://brownbears.tistory.com/425
            config = config_models.Setting.objects.last()
            emd_targets = config.emd_targets.split(',')
            print('emd targets', emd_targets)
            for juso in emd_targets:
                print(juso)
                sido, sgg, emd = juso.split()
                q.add(Q(sido= sido, sgg= sgg, emd= emd), q.OR)

            # 읍면동 타겟이 없을 때 시도 타겟으로 대체
            # 한 달에 한 번? 정도 전체 돌릴 때 사용
            # 이것도 config의 setting에서 가져오도록 함
            # 구현해야 함
            ### region_targets = config.region_targets.split(',')
            ### if len(settings.EMD_TARGETS) == 0:
            ###     for target in settings.REGION_TARGETS:
            ###         q.add(Q(sido= target), q.OR)


            total_count = rawarticle_models.Cluster.objects.filter(q).count()
            done_count = rawarticle_models.Cluster.objects.filter(q).filter(
                article_collected_date= timezone.now().date()
            ).count()

            percent = done_count / total_count * 100
            print(
                '|Total : ' + str(total_count) + ' / Done : ' + str(done_count) + ' / % Done : ' + str(int(percent)) + '%'
            )

            orderings = ['lgeo', 'lat', 'lon', 'count', 'emd', ]
            desc = ['-', '']

            random.shuffle(orderings)
            random.shuffle(desc)

            order = desc[0] + orderings[0]
            target = rawarticle_models.Cluster.objects.filter(
                is_collecting= False,
            ).filter(q).exclude(
                article_collected_date= timezone.now().date()
            ).order_by(
                order
            ).first()

            if not target:
                # 할게 없지만 collecting 중인 게 있을 수 있음
                # 진짜 없는가 확인
                maybe_collecting = rawarticle_models.Cluster.objects.filter(q).exclude(
                    article_collected_date= timezone.now().date()
                ).first()
                if maybe_collecting:
                    m = maybe_collecting
                    rp('maybe collecting : ' + m.sido + ' ' + m.sgg + ' ' + m.emd + ' ' + m.lgeo, msg_type='NOTICE')
                    rp('Sleeping 60 seconds')
                    time.sleep(60)
                    continue
                else:
                    rp('Collecting done. Wait 60 seconds')
                    time.sleep(60)
                    return

            target.is_collecting = True
            target.article_collection_start_time = timezone.now()
            target.save()

            # if percent > 99 or total_count - done_count < 2:
            #     rp('Almost done. Stop except one ec.', msg_type='IMPORTANT_NOTICE')
            #     # 99%면 거의 다 한 것이므로 2개 남겨놓고 다 스톱시킴
            #     rawarticle_models.ArticleCollectorTargetCount.objects.create(
            #         us_east_1= 1,
            #         us_east_2= 1,
            #     )


            try:
                if target.lgeo == '':
                    rp('Empty lgeo. Skip')
                    target.is_collecting = False
                    target.article_collection_start_time = timezone.now()
                    target.article_collected_date = timezone.now().date()
                    target.article_collection_end_time = timezone.now()
                    target.final_url = None
                    target.done_url = None
                    target.save()
                    continue
                self._collect(target)
            except Exception as e:
                target.is_collecting = False
                target.save()
                if (str(e) == 'result is empty'):
                    rawarticle_models.BlockedIp.objects.create(
                        instance_id= settings.EC2_INSTANCE_ID,
                        ip= settings.SERVER_IP,
                        aws_region= settings.EC2_AWS_REGION,
                        launch_time_when_blocked= settings.EC2_LAUNCH_TIME,
                    )
                    self.aws_util.stop_instance(
                        settings.EC2_AWS_REGION,
                        settings.EC2_INSTANCE_ID
                    )
                    self._wait_for_cooling_time(settings.FULL_BREAK_WHEN_BLOCKED_IN_MIN)

                    # inst = rawarticle_models.RegionInstanceMap.objects.filter(
                    #     instance_id= settings.EC2_INSTANCE_ID
                    # ).first()
                    # if not inst:
                    #     rp('No instance found for ' + settings.EC2_INSTANCE_ID, msg_type='IMPORTANT_NOTICE')
                    #     continue

                    # launch_time = rawarticle_models.RegionInstanceMap.objects.filter(
                    #     instance_id= settings.EC2_INSTANCE_ID,
                    # ).first().launch_time
                    # rp('launch_time : ' + str(launch_time), msg_type='NOTICE')
                    # blocked_ip.launch_time_when_blocked = launch_time
                    # blocked_ip.save()

                    # blocked_today = rawarticle_models.BlockedIp.objects.filter(
                    #     instance_id= settings.EC2_INSTANCE_ID,
                    #     created_date= timezone.now().date()
                    # ).first()
                    # if blocked_today:
                        # # 10분 * 4
                        # self._wait_for_cooling_time(settings.FULL_BREAK_WHEN_BLOCKED_IN_MIN * 4)
                        # rp('Blocked today. Terminate : ' + inst.aws_region + ' ' + settings.EC2_INSTANCE_ID + ' ' + settings.SERVER_IP, msg_type='IMPORTANT_NOTICE')
                        # watcher.terminate_instance(settings.EC2_INSTANCE_ID)
                        # self._wait_for_cooling_time(settings.FULL_BREAK_WHEN_BLOCKED_IN_MIN)
                        # continue

                    # 40분의 쿨타임을 가지도록 함
                    # self._wait_for_cooling_time(settings.FULL_BREAK_WHEN_BLOCKED_IN_MIN * 40)
                    # watcher.stop_instance(settings.EC2_INSTANCE_ID)
                    # self._wait_for_cooling_time(settings.FULL_BREAK_WHEN_BLOCKED_IN_MIN)

                else:
                    rp('Other Exception: ' + str(e), msg_type='ERROR')
                    self.aws_util.stop_instance(
                        settings.EC2_AWS_REGION,
                        settings.EC2_INSTANCE_ID
                    )
                    self._wait_for_cooling_time(settings.FULL_BREAK_WHEN_BLOCKED_IN_MIN)
                    raise e

            target.is_collecting = False
            target.article_collected_date = timezone.now().date()
            target.article_collection_end_time = timezone.now()
            target.final_url = target.done_url
            target.done_url = None
            target.save()
            # rp('Done collecting ' + target.sido + ' ' + target.sgg + ' ' + target.emd + ' ' + target.lgeo + ' ' + target.final_url, msg_type='NOTICE')


            elapsed_time = int(time.time() - start_time)
            rp('Elapsed time : ' + str(elapsed_time) + ' seconds')
            rp('working_seconds : ' + str(working_seconds) + ' seconds' )
            rp('Will be sleep after ' + str(working_seconds - elapsed_time) + ' seconds')

            if elapsed_time > working_seconds:
                rp('Elapsed time is over ' + str(working_seconds) + ' seconds.')
                self._wait_for_cooling_time(settings.BREAK_TIME_IN_MIN)
                continue

            dt_util.long_sleep_random()

    def _collect(self, cluster):
        rp('Collect article of Cluster : ' + cluster.sido + ' ' + cluster.sgg + ' ' + cluster.emd + ' ' + cluster.lgeo)
        params = {
            'itemId': cluster.lgeo,
            'lgeo': cluster.lgeo,
            'mapKey': '',
            'cortarNo': cluster.parent,
            'showR0': '',
            'z': 12,
            "rletTpCd": "APT%3AOPST%3AVL%3AABYG%3AOBYG%3AJGC%3AJWJT%3ADDDGG%3ASGJT%3AHOJT%3AJGB%3AOR%3AGSW%3ASG%3ASMS%3AGJCG%3ASG%3AGM%3ATJ%3AAPTHGJ",
            'tradTpCd': 'A1%3AB1%3AB2%3AB3',
        }
        curlreq.get_with_more(
            'https://m.land.naver.com/cluster/ajax/articleList',
            params,
            cluster,
            self.__create_article
        )

    def _wait_for_cooling_time(self, minunte):
        randomized = dt_util.get_random_number(
            from_no= minunte * 0.8,
            to_no=   minunte * 1.2,
        )
        rp('Cooling for ' + str(randomized) + ' minutes')
        time.sleep(randomized * 60)

    def __create_article(self, result_obj, cluster):
        for article in result_obj['body']:
            got, created = rawarticle_models.ProtoArticle.objects.get_or_create(
                article_id= article['atclNo'],
                created_date= timezone.now(),
                defaults= {
                    'lgeo': cluster.lgeo,
                    'cortarNo': cluster.parent,
                    'sido': cluster.sido,
                    'sgg': cluster.sgg,
                    'emd': cluster.emd,
                    'list_text': article
                }
            )
            if created:
                pass
                # rp('[RO] ' + got.article_id + ' created.')
            else:
                rp('[RO] article number already exists ' + got.article_id + ' ' +  str(got.created_date))
