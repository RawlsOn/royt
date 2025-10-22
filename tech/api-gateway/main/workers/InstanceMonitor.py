from django.conf import settings

from common.util.romsg import rp
import subprocess
import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

# from copy import copy
from datetime import datetime, date, timedelta
from django.utils import timezone as django_timezone
from pytz import timezone
from django.db.models import QuerySet

import common.util.datetime_util as dt_util
import common.util.str_util as str_util
from common.util.logger import RoLogger
logger = RoLogger()
from argparse import Namespace
from common.util import curlreq
import rawarticle.models as rawarticle_models
from common.util.AwsUtil import AwsUtil
# pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

# ./manage.py run_article_collector
# /home/admin/Works/mkay/onenlc/api-gateway/venv/bin/python /home/admin/Works/mkay/onenlc/api-gateway/manage.py run_article_collector
# ssh -i ~/.ssh/aws-ro-seoul.pem -o ServerAliveINterval=10 ec2-user@3.39.230.17

class InstanceMonitor(object):

    def __init__(self, args={}):
        self.args = args
        self.aws_util = AwsUtil()

    def run(self):
        print('run InstanceMonitor')
        # self.restore_default_setting()
        while True:
            try:
                self.update_instance_monitoring()
                self.change_status_of_instances()
                self.run_instances_stopped()
                self.fix_not_working_cluster()
                if settings.RUN_LIST_COLLECTOR:
                    self.stop_instances_running_longer_than(minutes=30)
                    self.watch_article_collection()
                print('InstanceMonitor: Sleeping for 87 seconds...')
                time.sleep(87)
            except Exception    as e:
                rp(str(e), msg_type='NOTICE')
                raise e

    def run2(self):
        print('run 2')
        self.check_logs()

    def show_instances(self):
        self.update_instance_monitoring()
        print('show running instances...')
        for instance in self.instances:
            if instance['state'] == 'running':
                print('\n\n')
                print(''.join([
                    'ssh -o UserKnownHostsFile=/dev/null',
                    ' -o StrictHostKeyChecking=no -o ServerAliveINterval=10',
                    ' -i ~/.ssh/',
                    instance['key_name'],
                    '.pem',
                    ' admin@',
                    instance['ip'],
                ]))

    def terminate_all_instances(self):
        self.update_instance_monitoring()
        print('terminate all instances...')
        for instance in self.instances:
            self.aws_util.terminate_instance(
                instance['region'],
                instance['instanceId']
            )

    def restore_default_setting(self):
        default = rawarticle_models.ArticleCollectorTargetCount.objects.first().__dict__
        del default['_state']
        rawarticle_models.ArticleCollectorTargetCount.objects.all().delete()
        rawarticle_models.ArticleCollectorTargetCount.objects.create(
            **default
        )

    def watch_article_collection(self):
        q = Q()
        # https://brownbears.tistory.com/425
        for juso in settings.EMD_TARGETS:
            sido, sgg, emd = juso.split()
            q.add(Q(sido= sido, sgg= sgg, emd= emd), q.OR)

        # 읍면동 타겟이 없을 때 시도 타겟으로 대체
        # 한 달에 한 번? 정도 전체 돌릴 때 사용
        if len(settings.EMD_TARGETS) == 0:
            for target in settings.REGION_TARGETS:
                q.add(Q(sido= target), q.OR)

        total_count = rawarticle_models.Cluster.objects.filter(q).count()
        done_count = rawarticle_models.Cluster.objects.filter(q).filter(
            article_collected_date= django_timezone.now().date()
        ).count()

        percent = done_count / total_count * 100
        rp(
            str(done_count) + ' / ' + str(total_count) + ' | ' + str(int(percent)) + '%',
            msg_type='NOTICE'
        )


    def update_instance_monitoring(self):
        response = self.aws_util.describe_all_instances()
        instances = self.aws_util.groom_described_instances(response)

        count_map = {
            'running': 0,
            'stopped': 0,
            'pending': 0,
            'stopping': 0,
            'terminated': 0,
        }
        self.instances = instances
        for instance in self.instances:
            if instance['state'] == 'shutting-down':
                continue
            count_map[instance['state']] += 1

        return count_map

    def get_instance_stat_count(self):
        return self.update_instance_monitoring()

    def change_status_of_instances(self):
        # 타겟 갯수에 맞추어 인스턴스를 늘리거나 줄인다
        target = rawarticle_models.ArticleCollectorTargetCount.objects.last().__dict__
        del target['_state']
        del target['id']
        del target['created_at']
        del target['updated_at']
        del target['created_date']

        # pp.pprint(target)
        # pp.pprint(self.instances)

        live_count_by_region = {}

        for instance in self.instances:
            if instance['state'] == 'running' or instance['state'] == 'pending' or instance['state'] == 'stopping' or instance['state'] == 'stopped':
                if instance['region'] not in live_count_by_region:
                    live_count_by_region[instance['region']] = 0
                live_count_by_region[instance['region']] += 1

        # pp.pprint(live_count_by_region)

        for region, target_count in target.items():
            region = t(region)
            diff = live_count_by_region.get(region, 0) - target_count
            if diff < 0:
                self._create_and_start_instances(region, abs(diff))
            elif diff > 0:
                self._terminate_instances(region, diff)

    def run_instances_stopped(self):
        # stopped 상태의 인스턴스를 실행한다
        for instance in self.instances:
            if instance['state'] == 'stopped':
                rp('run instance ' + instance['region'] + ' ' + instance['instanceId'])
                self.aws_util.start_instance(
                    instance['region'], instance['instanceId']
                )

    def stop_instances_running_longer_than(self, minutes=30):
        from_min = minutes - 3
        to_min = minutes + 13
        random_min = dt_util.get_random_number(from_min, to_min)
        for instance in self.instances:
            if instance['state'] == 'running':
                gap = (
                    django_timezone.now() - timedelta(minutes=random_min)
                ).replace(tzinfo=timezone('Asia/Seoul'))
                if instance['launch_time'].replace(tzinfo=timezone('Asia/Seoul')) < gap:
                    rp('Stopping instance ' + instance['region'] + ' ' + instance['instanceId'], msg_type='NOTICE')
                    self.aws_util.stop_instance(
                        instance['region'],
                        instance['instanceId']
                    )
                    continue

    def stop_all_instances(self, minutes=30):
        self.update_instance_monitoring()
        for instance in self.instances:
            if instance['state'] == 'running':
                rp('stop ' + instance['region'] + ' ' + instance['instanceId'])
                self.aws_util.stop_instance(
                    instance['region'],
                    instance['instanceId']
                )

    def _create_and_start_instances(self, region, count):
        rp('create and run instances ' + region + ' ' + str(count))
        image = rawarticle_models.BaseImage.objects.filter(region=region).first()
        if not image:
            rp('image not found: ' + region, msg_type='ERROR')
            return
        if not self.aws_util.clients.get(region, None):
            rp('client not found: ' + region, msg_type='ERROR')
            return

        response = self.aws_util.clients[region].run_instances(
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/xvda',
                    'Ebs': {

                        'DeleteOnTermination': True,
                        'VolumeSize': 20,
                        'VolumeType': 'gp2'
                    },
                },
            ],
            ImageId= image.image_name,
            InstanceType= image.instance_type,
            MaxCount= count,
            MinCount= count,
            KeyName= image.key_name,
            Monitoring={
                'Enabled': False
            },
            SecurityGroupIds=[
                image.security_group,
            ],
        )

    def _terminate_instances(self, region, count):
        terminated_count = 0
        for instance in self.instances:
            if instance['state'] == 'running' and terminated_count < count and instance['region'] == region:
                self.aws_util.terminate_instance(
                    instance['region'],
                    instance['instanceId']
                )
                terminated_count += 1


        print('terminate-instances', region, count)

    def fix_not_working_cluster(self):
        collectings = rawarticle_models.Cluster.objects.filter(
            is_collecting=True
        ).order_by('article_collection_start_time')

        targets = []
        for col in collectings:
            # rp('checking ' + col.sgg + ' ' + col.emd + ' ' + col.lgeo)
            # 시작한 지 한시간이 넘은 것은 중간에 끊긴 것으로 간주
            # 작업대상에 포함시킨다
            if col.article_collection_start_time < django_timezone.now() - timedelta(hours=1):
                targets.append(col)

        for target in targets:
            target.is_collecting = False
            target.save()
            rp('fixing target ' + target.sgg + ' ' + target.emd + ' ' + target.lgeo)

def t(unberbar):
    return unberbar.replace('_', '-')