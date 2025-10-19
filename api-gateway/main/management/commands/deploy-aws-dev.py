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
        print('deploy aws dev...')

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
        print('base instance id: ' + self.base_instance_id)
        base_instance_public_dns = self.aws_util.get_instance_public_dns(
            instance_id= self.base_instance_id
        )

        self.aws_util.wait_for_instances_creation([self.base_instance_id])

        # 베이스 인스턴스에서 빌드
        print('ssh -i ~/.ssh/vf-dev-1.pem ' + base_instance_public_dns)
        os.system(' '.join([
            './shell/build-aws-dev.sh',
            base_instance_public_dns,
            self.base_instance_id
        ]))

        self.aws_util.stop_instances([self.base_instance_id])
        # self.aws_util.remove_instances([self.base_instance_id])