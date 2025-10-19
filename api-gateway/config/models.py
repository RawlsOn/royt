from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db import models
import base.models as base_models
import common.util.model_util as model_util
import uuid

import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

class SEO(base_models.RoBase):
    title = models.CharField(max_length= 255)
    desc = models.CharField(max_length= 255)
    keywords = models.CharField(max_length= 255)

    image_url = models.FileField(
        blank=True, null=True,
        upload_to=model_util.upload_to_SEO
    )

    @property
    def image_url_wo_expire(self):
        try:
            return self.image_url.url.split('?')[0]
        except Exception as e:
            return self.image_url.url

    class Meta:
        # first로 얻을 때 가장 오래된 것이 나옴
        ordering = ('-created_at', )

# 안 쓸 거 같지만..
class Screen(base_models.RoBase):
    title = models.CharField(max_length= 16)
    score = models.PositiveSmallIntegerField()

class BaseSetting(base_models.RoBase):
    content = models.JSONField(blank=True, null=True)

############
# {
#     "screen": {
#         "color": {
#             "primary": "blue-12",
#             "secondary": "green-12",
#             "accent": "purple-12",

#             "positive": "btc-blue",
#             "negative": "red-12",
#             "info": "blue-grey-6",
#             "warning": "amber-10"
#         }
#     }
# }