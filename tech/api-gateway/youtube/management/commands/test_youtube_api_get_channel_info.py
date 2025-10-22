"""
YouTube API get_channel_info
"""
import json
from django.core.management.base import BaseCommand
from youtube.youtube_api_wrapper import YouTubeAPIWrapper

import pprint
pp = pprint.PrettyPrinter(indent=2)  # pp.pprint()

class Command(BaseCommand):
    help = 'YouTube API X get_channel_info'

    def add_arguments(self, parser):
        parser.add_argument(
            'channel_identifier',
            type=str,
            help=''
        )
        parser.add_argument(
            '--no-db',
            action='store_true',
            help=''
        )

    def handle(self, *args, **options):
        channel_identifier = options['channel_identifier']
        save_to_db = not options['no_db']

        youtube_api = YouTubeAPIWrapper(save_to_db=save_to_db)

        channel_info = youtube_api.get_channel_info(channel_identifier)

        pp.pprint(channel_info)