from datetime import datetime, date, timedelta
from django.conf import settings
import json

class ProgressWatcher(object):

    def __init__(self, total_count, logger, info='', gap= 5):
        self.total_count = total_count
        self.logger = logger
        self.info = info
        self.gap = gap

    def log(self, current_count, info=None):
        if info:
            self.info = info
        self.current_count = current_count
        percent = current_count/self.total_count*100
        output = "\t".join([
            str(current_count) + ' / ' + str(self.total_count),
            "{:.5f}".format(percent) + '%',
            self.info,
        ])
        if current_count % self.gap == 0:
            self.logger.INFO(output)