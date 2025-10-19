from django.conf import settings

import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from datetime import datetime, date, timedelta
from django.utils import timezone
from common.util.logger import RoLogger
from common.util.ProgressWatcher import ProgressWatcher
logger = RoLogger()

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

import boto3
from django.utils import timezone
import time

# ./backend/venv/bin/python ./backend/manage.py add_instances_to_lb

from common.util.AwsUtil import AwsUtil

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--instance_id',
            type=str,
            default= ''
        )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        self.run()

    def run(self):
        self.aws_util = AwsUtil(self.options)
        print('deploy dev...')

        # 베이스 이미지로부터 베이스 인스턴스를 생성
        if self.options['instance_id'] == '':
            self.base_instance = self.aws_util.create_a_instance_from_image(
                image_id= settings.AWS_BASE_AMI_ID,
                instance_type= 'm4.large',
                name= 'valoan2-base'
            )
            self.base_instance_id = self.base_instance.id
        else:
            self.base_instance_id = self.options['instance_id']

        # 생성된 인스턴스의 dns를 저장
        print('base instance id: ' + )
        base_instance_public_dns = self.aws_util.get_instance_public_dns(
            instance_id= self.base_instance_id
        )


        self.aws_util.wait_for_instances_creation([self.base_instance_id])

        # 베이스 인스턴스에서 빌드
        self.build(base_instance_public_dns)

        self.aws_util.stop_instances([self.base_instance_id])

    def build(self, instance_public_dns):
        os.system(' '.join([
            './shell/build-aws-dev.sh',
            instance_public_dns,
            self.base_instance.id
        ]))

    # def prepare(self):
    #     print('prepare...')
    #     print('load boto3...')
    #     profile_name = 'vf-dev-1'
    #     boto3.setup_default_session(profile_name= profile_name)
    #     self.session = boto3.session.Session(profile_name= profile_name)
    #     self.ec2_client = self.session.client("ec2", region_name='ap-northeast-2')
    #     self.ec2 = boto3.resource("ec2", region_name='ap-northeast-2')
    #     self.base_instance_ids = []

    # def create_instance_from_base_image(self):
    #     print('create_instance_from_base_image...')

    #     resp = self.ec2.create_instances(
    #         ImageId=settings.AWS_BASE_AMI_ID,
    #         MinCount=1,
    #         MaxCount=1,
    #         InstanceType= 'm4.large',
    #         SecurityGroupIds= [ settings.AWS_SECURITY_GROUP_ID ],
    #         Monitoring= { 'Enabled': True },
    #         Placement= { 'AvailabilityZone': settings.AWS_AVAILABILITY_ZONE }
    #     )
    #     print(resp)
    #     for instance in resp:
    #         self.base_instance_ids.append(instance.id)
    #     print('self.base_instance_ids', self.base_instance_ids)

    # def wait_for_instance_creation(self, targets):
    #     print('wait_for_instance_creation')
    #     while True:
    #         resp = self.ec2_client.describe_instances(
    #             InstanceIds= targets
    #         )
    #         print(resp)
    #         states = [x['State']['Name'] for x in resp["Reservations"][0]['Instances']]
    #         print(states)
    #         if all(x == 'running' for x in states):
    #             self.base_instance_dns = 
    #             break
    #         logger.INFO('sleep for 5 seconds...')
    #         time.sleep(5)
