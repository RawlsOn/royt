# edit at 2024-05-26
# cp /Users/kimmyounghoon/Works/mkay/common/api-gateway/common/util/* ./api-gateway/common/util/

import random
import io, time
from django.utils import timezone
from django.conf import settings
from common.util.romsg import rp
from datetime import datetime, date, timedelta

def get_random_number(from_no=3, to_no=20):
    got = random.uniform(from_no, to_no)
    return round(got, 1)

def get_random_sec(from_no=1.1, to_no=3.8):
    got = random.uniform(from_no, to_no)
    return round(got, 1)

def long_sleep_random():
    sleep_time = get_random_number(
        from_no= 60,
        to_no= 120
    )
    rp('sleeping... (' + str(sleep_time) + ' seconds)')
    time.sleep(sleep_time)

def ten_min_sleep_random():
    sleep_time = get_random_number(
        from_no= 500,
        to_no= 700
    )
    rp('sleeping... (' + str(sleep_time) + ' seconds)')
    time.sleep(sleep_time)

def sleep_random(from_no= 3, to_no= 20):
    sleep_time = get_random_number(from_no, to_no)
    rp('sleeping... (' + str(sleep_time) + ' seconds)')
    time.sleep(sleep_time)

def sleep(sleep_time= 5, reason= ''):
    rp(str(reason) + ' sleeping... (' + str(sleep_time) + ' seconds)')
    time.sleep(sleep_time)

def pretty_date(time=False, now=None):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    if not now:
        now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 300:
            return "방금 전"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + "분 전"
        if second_diff < 86400: # 12 시간
            return str(int(second_diff / 3600)) + "시간 전"
    if day_diff == 1:
        return "어제"
    if day_diff < 7:
        return str(int(day_diff)) + "일 전"
    if day_diff < 31:
        return str(int(day_diff / 7)) + "주 전"
    if day_diff < 365:
        return time.strftime("%-m월 %-d일")
    return time.strftime("%Y년 %-m월")

def now():
    return timezone.now()

def tz_now():
    return timezone.now()

def now_str():
    return timezone.now().strftime("%Y-%m-%d %H:%M:%S")

def now_str_nospace():
    return timezone.now().strftime("%Y%m%d%H%M%S")

def get_monday():
    today = timezone.now()
    return today - timedelta(today.weekday())

def sec_to_str(seconds):
    h=seconds//3600
    m=(seconds%3600)//60
    # d=["{} hours {} mins {} seconds".format(a, b, c)]
    if h == 0.0:
        return str(int(m)) + '분'

    return str(int(h)) + '시간 ' + str(int(m)) + '분'

def get_today():
    return timezone.now().date()

def get_today_str():
    return timezone.now().strftime("%Y-%m-%d")

def today():
    return timezone.now().date()

def this_month():
    return timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()

def today_00():
    return timezone.now().replace(hour=0, minute=0, second=0)

def today_str():
    return timezone.now().strftime("%Y-%m-%d")

def fix_date_str(date_str):
    # '19900309' -> '1990-03-09'

    if type(date_str) == int: date_str = str(date_str)

    if date_str == '-': return None

    if date_str is None: return None

    if date_str.strip() == '': return None

    if date_str == '2014-02-29': date_str = '2014-02-28'
    if date_str == '20140229': date_str = '20140228'
    if date_str == '2013-04-31': date_str = '2013-04-30'
    if date_str == '20130431': date_str = '20130430'

    if isinstance(date_str, int):
        date_str = str(date_str)

    if isinstance(date_str, date):
        year, month, day = date_str.strftime('%Y-%m-%d').split('-')
    elif '-' in date_str:
        year, month, day = date_str.split('-')
    else:
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:]

    if year == '2014' and month == '02' and day == '29':
        day = '28'
    if month in ['02','04','06','09','11'] and day == '31':
        day = '30'
    if month == '02' and day in ['30', '31']:
        day = '28'

    if year == '0': return None

    if year == '': return None

    # print('year, month, day', year, month, day)

    if month == '00': month = '01'
    if month == '': month = '01'
    if day == '00': day = '01'

    month = month.replace('.', '')
    day = day.replace('.', '')

    if year.isnumeric() == False: return None
    if month.isnumeric() == False: return None
    if day.isnumeric() == False: return None

    if int(month) > 12: return None

    if year[0] == '0': return None

    if len(year) != 4: return None
    if len(month) != 2: return None
    if len(day) != 2: return None

    if int(month) > 12: day = '01'
    if int(day) > 31: day = '01'

    return year + '-' + month + '-' + day

def days_ago(ago_no=1):
    d = timedelta(days = ago_no)
    return now() - d

def minutes_ago(ago_no=1):
    d = timedelta(minutes = ago_no)
    return now() - d

def date_to_datetime(date):
    return datetime.combine(date, datetime.min.time())

