from django.db import models

import base.models as base_models

class Board(base_models.RoBase):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)

    class Meta:
        # first로 얻을 때 가장 최근 것이 나옴
        ordering = ('-created_at', )

    def __str__(self):
        return self.title
