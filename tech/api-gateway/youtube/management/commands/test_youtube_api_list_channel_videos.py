"""
YouTube API list_channel_videos
"""
import json
from django.core.management.base import BaseCommand
from youtube.youtube_api_wrapper import YouTubeAPIWrapper

import pprint
pp = pprint.PrettyPrinter(indent=2)  # pp.pprint()

class Command(BaseCommand):
    help = 'YouTube API X list_channel_videos'

    def add_arguments(self, parser):
        parser.add_argument(
            'channel_identifier',
            type=str,
            help='YouTube 채널 ID 또는 핸들 (예: @channelname 또는 UCxxxxx)'
        )
        parser.add_argument(
            '--no-db',
            action='store_true',
            help='DB에 저장하지 않음'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='상세한 로그 출력'
        )

    def handle(self, *args, **options):
        channel_identifier = options['channel_identifier']
        save_to_db = not options['no_db']
        verbose = options['verbose']

        youtube_api = YouTubeAPIWrapper(save_to_db=save_to_db, verbose=verbose)

        videos = youtube_api.list_channel_videos(channel_identifier)

        if verbose:
            pp.pprint(videos)