from django.db import models

import user.models as user_models

from rticler.models.base_post import BasePost
from rticler.models.board import Board

class TempArticle(BasePost):

    user = models.ForeignKey(
        user_models.CustomUser,
        on_delete= models.CASCADE, null= True
    )

class Article(BasePost):

    user = models.ForeignKey(
        user_models.CustomUser,
        on_delete= models.CASCADE, null= True
    )

    board = models.ForeignKey(
        Board,
        on_delete= models.CASCADE, null= True
    )

    temp_article = models.OneToOneField(
        TempArticle,
        on_delete= models.CASCADE, null= True, blank=True
    )

# class BasePost(base_models.RoBase):
#     title = models.CharField(max_length=255)
#     content = models.TextField(blank=True, null=True)

#     class Meta:
#         # first로 얻을 때 가장 최근 것이 나옴
#         ordering = ('-created_at', )
