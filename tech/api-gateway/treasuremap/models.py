from django.db import models
import base.models as base_models

from django.conf import settings

class Note(base_models.RoBase):
    text = models.TextField(blank=True, null=True)