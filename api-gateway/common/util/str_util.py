# edit at 2024-02-29
# cp /Users/kimmyounghoon/Works/mkay/common/api-gateway/common/util/* ./api-gateway/common/util/

import io, sys, time, os, glob, pprint, json, re, shutil, ntpath, csv

import urllib.parse as urlparse
import re
from django.utils import timezone
import common.util.datetime_util as dt_util

class ProgressShower(object):

    def __init__(self, gap=100, info=''):
        self.gap = gap
        self.info = info
        self.now = 0
        self.total = 0
        self.start_time = dt_util.now_str()
        self.TIME_PERCENT_2 = None
        self.LAST_TIME_PERCENT_2 = None
        self.ELAPSED_FOR_PERCENT_2 = None
        self.ELAPSED_UNTIL = 0

    def init(self):
        self.__init__()

    def show(self):
        if (self.total == 0): raise Exception('Total should be set to non-zero.')
        percent = int(self.now/self.total*100)
        self.LAST_TIME_PERCENT_2 = self.TIME_PERCENT_2
        self.TIME_PERCENT_2 = timezone.now()

        estimation = 0
        # if self.TIME_PERCENT_2 is not None and self.LAST_TIME_PERCENT_2 is not None:
        #     self.ELAPSED_FOR_PERCENT_2 = self.TIME_PERCENT_2 - self.LAST_TIME_PERCENT_2
        #     self.ELAPSED_UNTIL += self.ELAPSED_FOR_PERCENT_2.total_seconds()
        #     if percent != 0:
        #         estimation = (100 - percent) / percent * self.ELAPSED_UNTIL

        output = "\t".join([
            self.start_time,
            dt_util.now_str(),
            self.info,
            str(self.now) + ' / ' + str(self.total),
            str(percent) + '%',
            # str(int(estimation)) + ' seconds remain.',
            # str(int(self.ELAPSED_UNTIL)) + 'secs',
        ])

        if self.now % self.gap == 0:
            print(output)

        self.now += 1

def print_progress(now, total, info='', gap=5):
    percent = now/total*100
    output = "\t".join([
        dt_util.now_str(),
        info,
        str(now) + ' / ' + str(total),
        "{:.5f}".format(percent) + '%'
    ])
    if now % gap == 0:
        print(output)

def decode_url(string):
    return urlparse.unquote(string)

def camel_to_dash(string):
    return re.sub(r'(?<!^)(?=[A-Z])', '-', string).lower()

def two_dict_dup_key_exist(dict1, dict2):
    for key in dict1.keys():
        if key in dict2.keys():
            return True, key
    return False, None

def two_dict_dup_key_exist_and_diff_value(dict1, dict2):
    for key in dict1.keys():
        if key in dict2.keys():
            if dict1[key] != dict2[key]:
                if dict1[key] is None or dict2[key] is None:
                    continue
                if dict1[key] == '' or dict2[key] == '':
                    continue
                return True, key, str(dict1[key]) + ' / ' + str(dict2[key])
    return False, None, None

def float_range(start, end, step=0.1, precision=2):
    while start < end:
        yield f"%.{precision}f" % start
        start += step

def line_count(file, encoding='utf-8'):
    with open(file, 'r', encoding=encoding) as f:
        return sum(1 for _ in f)

def float_str(f, digit=2):
    if f is None: return None
    if digit == 2:
        return f"{f:.2f}"

    if digit == 6:
        return f"{f:.6f}"