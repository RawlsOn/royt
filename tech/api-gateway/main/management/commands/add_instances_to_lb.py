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

from common.util.AwsUtil import AwsUtil

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--instance_id',
            type=str,
            required=True
        )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        self.run()

    def run(self):
        self.aws_util = AwsUtil(self.options)

        self.instances_to_remove = self.aws_util.get_instances_of_load_balancer()
        print('instances_to_remove')
        pp.pprint(self.instances_to_remove)

        self.ami_name = 'valoan2-base' + '-' + timezone.now().strftime("%Y%m%d%-H%M%S")
        base_image = self.aws_util.create_a_image(
            base_instance_id= self.options['instance_id'],
            ami_name= self.ami_name
        )

        image_id = base_image['ImageId']
        # image_id = 'ami-09aeb8c5aa9f6d3c1'
        # image_id = 'ami-0e36ecc1fa46cd2e1'
        self.aws_util.wait_for_image_creation(image_id)

        instance_ids = self.aws_util.create_instances_from_image(
            image_id= image_id,
            instance_type= settings.AWS_INSTANCE_TYPE,
            name= 'valoan2-dl-' + timezone.now().strftime("%Y%m%d%-H%M%S"),
            qty= settings.AWS_LB_INSTANCE_COUNT
        )

        self.aws_util.wait_for_instances_creation(instance_ids)
        self.aws_util.add_to_lb_targets(instance_ids)
        self.aws_util.wait_until_every_intances_healthy_in_lb()
        if self.aws_util.is_every_instance_healthy_in_lb():
            self.aws_util.remove_instances(self.instances_to_remove)

        print('wait for 30 seconds...')
        time.sleep(30)
        self.aws_util.assert_instances_count_of_lb(int(settings.AWS_LB_INSTANCE_COUNT))