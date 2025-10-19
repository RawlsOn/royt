import base.models as base_models
from django.core.files import File
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError
from common.util.ProgressWatcher import ProgressWatcher
from common.util.logger import RoLogger
from django.utils import timezone
from datetime import datetime, date, timedelta
import io
import time
import os
import glob
import pprint
import json
import re
import shutil
import ntpath
pp = pprint.PrettyPrinter(indent=2)  # pp.pprint()
logger = RoLogger()

from common.util.AwsUtil import AwsUtil

class Command(BaseCommand):

    def add_arguments(self, parser):
        pass
        # parser.add_argument(
        #     '--note',
        #     required=False,  # seconds
        #     type=str
        # )
        # parser.add_argument(
        #     '--loop',
        #     default=False,
        #     type=lambda x: (str(x).lower() == 'true')
        # )
        # parser.add_argument(
        #     '--sleep_time',
        #     default=5,  # seconds
        #     type=str
        # )

    def handle(self, *args, **options):
        """ Do your work here """
        self.aws_util = AwsUtil(options)
        self.run()

    def run(self):
        logger.INFO('update_fe_version')
        self.instances = self.aws_util.get_healthy_instances_of_load_balancer()
        public_dns = self.aws_util.get_instance_public_dns(self.instances[0])
        logger.INFO(public_dns)

        command = ' '.join([
            'ssh',
            '-o', '\"StrictHostKeyChecking no\"',
            'ubuntu@' + public_dns,
            '"docker exec -u 0 valoan-v2_api-server_1 ./manage.py update_fev"'
        ])
        logger.INFO(command)
        os.system(command)
