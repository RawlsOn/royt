# edit at 2024-05-27
# cp /Users/kimmyounghoon/Works/mkay/common/api-gateway/common/util/* ./api-gateway/common/util/
from django.apps import apps
from datetime import datetime, date, timedelta

from common.util.RoPrinter import RoPrinter
printer = RoPrinter('model_util')
rp = printer.rp

import os
import logging
logger = logging.getLogger('apps')
from django.conf import settings
import uuid
import common.util.str_util as str_util

import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

def is_diff(me, new_entry):
    # compare all fields
    result = []
    for k, v in new_entry.items():
        if k == 'gijun_date' or k == 'gijun_date_str' or k == 'created_date' or k == 'created_at' or k == 'updated_at' or k == 'ro_gijun_date' or k == 'ro_gijun_date_str':
            continue
        if k == 'id' or k == 'bbox':
            continue
        if k == 'geom':
            me_geom = str(getattr(me, k))
            new_geom = str(v)
            if me_geom != new_geom:
                rp(f'[{me.id}] geom is different')
                result.append(f'{k}: {me_geom}->{new_geom}')

        # date일 경우 str으로 바꿔서 비교
        me_v = getattr(me, k)
        if isinstance(me_v, date):
            me_v = me_v.strftime('%Y-%m-%d')
        if isinstance(v, date):
            v = v.strftime('%Y-%m-%d')
        # float
        if isinstance(me_v, float):
            me_v = round(me_v, 6)
        if isinstance(v, float):
            v = round(v, 6)
        if me_v != v:
            rp(f'[{me.id}] {k} is different {getattr(me, k)} != {v}')
            result.append(f'{k}:{me_v}->{v}')

    if len(result) > 0:
        return True, result
    return False, None



def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None

def path_and_rename(instance, filename, field_name):
    logger.info('filename: ' + filename)
    ext = filename.split('.')[-1]

    new_filename = '{}.{}'.format(uuid.uuid4().hex, ext)

    if getattr(instance, 'user', False):
        new_filename = str(instance.user.pk) + '_' + new_filename

    ret = os.path.join(
        settings.AWS_S3_IMAGE_UPLOAD_TO,
        field_name,
        new_filename
    )
    # 이상하게 프린트나 logger 를 넣어야 동작을 함
    # 이건 진짜 말도 안 된다,,
    logger.info('AWS_STORAGE_BUCKET_NAME: ' + settings.AWS_STORAGE_BUCKET_NAME)
    logger.info('s3 path --------------- ' + ret)
    return ret

def upload_to_SEO(instance, filename):
    return path_and_rename(instance, filename, 'seo')

def upload_to_userimage(instance, filename):
    return path_and_rename(instance, filename, 'userimage')

def upload_to_usercss(instance, filename):
    return path_and_rename(instance, filename, 'usercss')

def bulk_create(targets, model, batch_size=1000):
    ps = str_util.ProgressShower(gap=1, info='BulkCreate ' + str(model))
    total = int(len(targets) / batch_size) + 1
    ps.total = total
    bulk = []
    for i in range(total):
        ps.show()
        start = i * batch_size
        end = (i + 1) * batch_size
        print('start', start, 'end', end)
        model.objects.bulk_create(targets[start:end], ignore_conflicts=True)

def add_to(target, to_add):
    if target is None or target == '':
        return to_add

    target_list = target.split(',')
    target_list.append(to_add)

    # remove duplicate
    target_list = list(set(target_list))

    # sort
    target_list.sort()

    return ','.join(target_list)

def m(app, model):
    return apps.get_model(app, model)

def show_values(model, field):
    targets = model.objects.all().values_list(field, flat=True).distinct().order_by()
    first_10 = [str(x) for x in list(targets)[:10]]
    last_10 = [str(x) for x in list(targets)[-10:]]
    samples = sorted(first_10 + last_10)
    max_len = 0
    for target in targets:
        max_len = max(max_len, len(str(target)))

    print(field, len(targets), f'max_len: {max_len}', samples)
