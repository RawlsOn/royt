from django.conf import settings

from common.util.romsg import rp
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

class InstanceWatcher(object):

    def __init__(self, args={}):
        self.args = args
        self.aws_util = AwsUtil()

    def run(self):
        pass
        # rp('Starting InstanceWatcher / IP ' + settings.SERVER_IP, msg_type='NOTICE')

        # ap_northeast_aws = AwsUtil(Namespace(**{
        #     'region_name': 'us-west-2',
        # }))
        # ret = ap_northeast_aws.describe_instances([
        #     'i-090774aa1b764030d',
        #     'i-0d628236f5d12da2b'
        # ])
        # pp.pprint(ret)
        # while True:
        #     self.fix_not_working_cluster()
        #     rp('fix_not_working_cluster() done; sleep 1 hour', msg_type='NOTICE')
        #     time.sleep(60 * 60)

        # self.stop_instances_running_longer_than_a_hour()

        # self.start_instances_where_region_not_finished()
        # aws_util = AwsUtil()
        # aws_util.start_instance('us-west-2', 'i-0fd077a8f406960be')
        # desc = aws_util.describe_instance('us-west-2', 'i-0fd077a8f406960be')
        # print(desc)

    def start_instances_where_region_not_finished(self):
        insts = rawarticle_models.RegionInstanceMap.objects.exclude(
            state= 'terminated'
        )
        for inst in insts:
            desc = self.aws_util.describe_instance(inst.aws_region, inst.instance_id)
            inst.state = desc['state']
            inst.save()
            if desc['state'] != 'stopped':
                continue

            target = rawarticle_models.Cluster.objects.filter(
                is_collecting= False,
                sido= inst.region
            ).exclude(
                article_collected_date= django_timezone.now().date()
            ).order_by(
                'lon'
            ).first()

            if target:

                total_count, done_count, ratio = self._get_done_ratio(inst)
                if total_count == 0:
                    rp('Something wrong,,, No cluster done for ' + inst.region, msg_type='IMPORTANT_NOTICE')
                elif total_count - done_count < 3:
                    rp(str(done_count) + ' / ' + str(total_count) + '] Almost done for ' + inst.aws_region + ' ' + inst.instance_id + ' for ' + inst.region + '\n' + 'Not starting instance...', msg_type='NOTICE')
                else:
                    # rp('Starting instance ' + inst.aws_region + ' ' + inst.instance_id + ' for ' + inst.region, msg_type='NOTICE')
                    self.aws_util.start_instance(inst.aws_region, inst.instance_id)
                    desc = self.aws_util.describe_instance(inst.aws_region, inst.instance_id)
                    inst.state = 'running'
                    inst.launch_time = desc['launch_time'].strftime('%Y-%m-%d %H:%M:%S')
                    inst.save()

    def stop_instances_running_longer_than_half_an_hour(self):
        insts = rawarticle_models.RegionInstanceMap.objects.exclude(
            state= 'terminated'
        )
        for inst in insts:
            desc = self.aws_util.describe_instance(inst.aws_region, inst.instance_id)
            an_hour_ago = (django_timezone.now() - timedelta(minutes=30)).replace(tzinfo=timezone('Asia/Seoul'))

            if desc['state'] == 'stopped':
                inst.state = 'stopped'
                inst.save()
                continue

            # print('--------------------------------')
            # print(desc['launch_time'])
            # print(django_timezone.now() - timedelta(hours=1))
            # print(desc['launch_time'].replace(tzinfo=timezone('Asia/Seoul')) < an_hour_ago)
            # print('--------------------------------')

            if desc['launch_time'].replace(tzinfo=timezone('Asia/Seoul')) < an_hour_ago:
                # rp('Stopping instance ' + inst.aws_region + ' ' + inst.instance_id + ' for ' + inst.region, msg_type='NOTICE')
                self.aws_util.stop_instance(inst.aws_region, inst.instance_id)
                inst.state = 'stopped'
                inst.save()
                continue
            # print(desc['launch_time'], timezone.now() + timedelta(hours=1))

    def stop_instances_done(self):
        insts = rawarticle_models.RegionInstanceMap.objects.exclude(
            state= 'terminated'
        )
        to_print = {}
        for inst in insts:
            desc = self.aws_util.describe_instance(inst.aws_region, inst.instance_id)
            if desc['state'] == 'stopped':
                continue
            total_count, done_count, ratio = self._get_done_ratio(inst)
            if total_count == done_count:
                # rp('Stopping instance ' + inst.aws_region + ' ' + inst.instance_id + ' for ' + inst.region, msg_type='NOTICE')
                self.aws_util.stop_instance(inst.aws_region, inst.instance_id)
            else:
                to_print[inst.region] = inst.region + ' Total: ' + str(total_count) + ' Done: ' + str(done_count) + ': ' + str(int(done_count / total_count * 100)) + '%'

        final_to_print = ['']
        for key, val in to_print.items():
            final_to_print.append(val)

        if len(final_to_print) == 1:
            rp('Nothing to Stop. Something wrong...', msg_type='NOTICE')
        elif len(final_to_print) > 1:
            rp('\n'.join(final_to_print), msg_type='NOTICE')

    def stop_instance(self, instance_id):
        aws_util = AwsUtil()
        inst = rawarticle_models.RegionInstanceMap.objects.get(
            instance_id=instance_id
        )
        aws_util.stop_instance(inst.aws_region, instance_id)

    def reboot_instance(self, instance_id):
        inst = rawarticle_models.RegionInstanceMap.objects.get(
            instance_id=instance_id
        )
        self.aws_util.reboot_instance(inst.aws_region, instance_id)

    def terminate_instance(self, instance_id):
        inst = rawarticle_models.RegionInstanceMap.objects.get(
            instance_id=instance_id
        )
        self.aws_util.terminate_instance(inst.aws_region, instance_id)

    def fix_not_working_cluster(self):
        collectings = rawarticle_models.Cluster.objects.filter(
            is_collecting=True
        ).order_by('article_collection_start_time')

        targets = []
        for col in collectings:
            # 시작한 지 한시간이 넘은 것은 중간에 끊긴 것으로 간주
            # 작업대상에 포함시킨다
            if col.article_collection_start_time < django_timezone.now() - timedelta(hours=1):
                targets.append(col)

        for target in targets:
            target.is_collecting = False
            target.save()
            rp('fixing target ' + target.sgg + ' ' + target.emd + ' ' + target.lgeo)

    def check_cluster_article_count(self):
        target_regions = [x.region for x in rawarticle_models.RegionInstanceMap.objects.all()]
        target_regions = list(set(target_regions))
        print(target_regions)

        for region in target_regions:
            clusters = rawarticle_models.Cluster.objects.filter(
                sido=region
            ).filter(
                article_collected_date=django_timezone.now().date()
            )
            print(region, clusters.count())
            for cluster in clusters:
                print(cluster.to_obj)
                dt_util.sleep_random()
            break

    def restart_all_instances(self):
        insts = rawarticle_models.RegionInstanceMap.objects.all()
        for inst in insts:
            result = self.aws_util.reboot_instance(inst.aws_region, inst.instance_id)
            print(result)

    def _get_done_ratio(self, instance):

        total_count = rawarticle_models.Cluster.objects.filter(sido= instance.region).count()
        done_count = rawarticle_models.Cluster.objects.filter(sido= instance.region).filter(article_collected_date= django_timezone.now().date()).count()
        if total_count == 0:
            return total_count, done_count, 0
        else:
            return total_count, done_count, int(done_count / total_count * 100)

