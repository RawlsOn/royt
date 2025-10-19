from django.conf import settings

import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from datetime import datetime, date, timedelta
from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import Group
from django.urls import reverse
from django.core.files import File
from django.contrib.auth import get_user_model

from random import randrange

# ./manage.py change_password --user_id 4f35b05f-b997-41d0-a7e7-8870c66888a2 --password 'vfd!!180802'

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--user_id',
            type= str,
            required= True
        )
        parser.add_argument(
            '--password',
            type= str,
            required= True
        )

    def handle(self, *args, **options):
        """ Do your work here """
        self.options = options
        # self.add_sample_users()
        User = get_user_model()
        found = User.objects.get(id= options['user_id'])
        found.set_password(options['password'])
        found.save()