from django.db import models
import base.models as base_models
import tenniscode.models as tenniscode_models

# ./manage.py makemigrations history
# ./manage.py migrate history --database=history

class ClubHistory(tenniscode_models.BaseClub):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', '기준일'], name='unique title 기준일')
        ]
        verbose_name= '클럽(히스토리)'
        verbose_name_plural= '클럽(히스토리)'

class ClubPrepared(tenniscode_models.BaseClub):
    class Meta:
        verbose_name= '클럽(준비)'
        verbose_name_plural= '클럽(준비)'

class PlayerHistory(tenniscode_models.BasePlayer):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'main_club_str', '기준일'], name='unique name main_club_str 기준일')
        ]
        verbose_name= '선수(히스토리)'
        verbose_name_plural= '선수(히스토리)'

class PlayerPrepared(tenniscode_models.BasePlayer):
    class Meta:
        verbose_name= '선수(준비)'
        verbose_name_plural= '선수(준비)'