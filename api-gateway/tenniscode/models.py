from django.db import models
import base.models as base_models

import urllib.parse
from django.conf import settings

# ./manage.py makemigrations tenniscode
# ./manage.py migrate tenniscode

class BaseClub(base_models.RoBase):
    title = models.CharField(max_length= 50)

    full_point = models.PositiveSmallIntegerField(default= 0)
    master_point = models.PositiveSmallIntegerField(default= 0)
    challenger_point = models.PositiveSmallIntegerField(default= 0)

    full_rank = models.PositiveSmallIntegerField(default= 0)
    master_rank = models.PositiveSmallIntegerField(default= 0)
    challenger_rank = models.PositiveSmallIntegerField(default= 0)

    players_count_having_performance = models.PositiveSmallIntegerField(default= 0)

    기준일 = models.DateField(db_index= True)
    기준일str = models.CharField(max_length= 8, blank=None, null=None, default= '20220101')

    def __str__(self):
        return self.title

    class Meta:
        abstract= True
        verbose_name= '클럽'
        verbose_name_plural= '클럽'

class Club(BaseClub):
    title = models.CharField(max_length= 50, unique= True, db_index= True)
    prev_full_rank = models.PositiveSmallIntegerField(default= 0)
    prev_master_rank = models.PositiveSmallIntegerField(default= 0)
    prev_challenger_rank = models.PositiveSmallIntegerField(default= 0)

    @property
    def link(self):
        return settings.FE_URL + '/club/' + self.title + '/'

    @property
    def link_escaped(self):
        return settings.FE_URL + '/club/' + urllib.parse.quote_plus(self.title) + '/'


class AnonClubComment(base_models.RoBase):
    club = models.ForeignKey(
        Club,
        on_delete= models.CASCADE, null=True,
        related_name= 'ClubS_comments'
    )
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    is_deleted = models.BooleanField(default= False)
    content = models.TextField()
    writer_name = models.CharField(max_length= 255)
    writer_pw = models.CharField(max_length= 16)
    writer_ip = models.CharField(max_length= 255)

class ClubProfile(base_models.RoBase):
    club = models.OneToOneField(
        Club,
        on_delete= models.CASCADE, null= True
    )
    image = models.URLField(blank=True, null=True)
    intro = models.CharField(max_length= 160, blank=True, null=True)
    location = models.CharField(max_length= 50, blank=True, null=True)

class BasePlayer(base_models.RoBase):
    name = models.CharField(max_length= 50, db_index=True)
    birthday = models.CharField(max_length= 6, default= '000000', null=True, blank=True)
    main_club_str = models.CharField(max_length= 50)

    challenger_point = models.PositiveSmallIntegerField(default= 0)
    master_point = models.PositiveSmallIntegerField(default= 0)
    full_point = models.PositiveSmallIntegerField(default= 0)

    class PlayerLevelChoices(models.TextChoices):
        상급자부_남자 = '상급자부(남자)'
        신인부_남자 = '신인부(남자)'

    player_level = models.CharField(max_length= 32, choices=PlayerLevelChoices.choices, blank= False, null= False)

    rank = models.PositiveSmallIntegerField(default= 0)

    기준일 = models.DateField(db_index= True)
    기준일str = models.CharField(max_length= 8, blank=None, null=None, default= '20220101')

    def __str__(self):
        return self.name

    class Meta:
        abstract= True
        verbose_name= '선수'
        verbose_name_plural= '선수'

class Player(BasePlayer):
    prev_rank = models.PositiveSmallIntegerField(default= 0)
    clubs = models.ManyToManyField(Club)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'main_club_str'], name='unique name main_club_str')
        ]

    @property
    def clubs_str(self):
        return ', '.join([str(x) for x in self.clubs.all().order_by('title')])

class PlayerProfile(base_models.RoBase):
    player = models.ForeignKey(
        Player,
        on_delete= models.CASCADE, null= True,
        related_name= 'playerS_Profile'
    )
    image = models.URLField(blank=True, null=True)
    intro = models.CharField(max_length= 160, blank=True, null=True)
    location = models.CharField(max_length= 50, blank=True, null=True)

class Competition(base_models.RoBase):
    title = models.CharField(max_length= 50)
    category = models.CharField(
        max_length= 32,
        default= '기타'
    )
    comp_type = models.CharField(max_length= 16, default= '기타')
    date = models.DateField()
    # 랭킹대회, 비랭킹대회, 지역대회, 초심자대회

    def __str__(self):
        return self.title + ' ' + self.category

    class Meta:
        verbose_name= '시합'
        verbose_name_plural= '시합'
        constraints = [
            models.UniqueConstraint(fields=['title', 'category'], name='unique title category')
        ]


class Performance(base_models.RoBase):
    competition = models.ForeignKey(
        Competition,
        on_delete= models.CASCADE, null= True,
        related_name= 'CompetitionS_Performance'
    )

    player = models.ForeignKey(
        Player,
        on_delete= models.CASCADE, null= True,
        related_name= 'playerS_Performance'
    )

    is_effective = models.BooleanField(default= False)

    point_type = models.CharField(max_length= 16, default='KATA')

    result = models.CharField(max_length=16)
    point = models.PositiveSmallIntegerField(default= 0)

    class PerformanceLevelChoices(models.TextChoices):
        상급자부_남자 = '상급자부(남자)'
        신인부_남자 = '신인부(남자)'

    performance_level = models.CharField(max_length= 32, choices=PerformanceLevelChoices.choices, blank= False, null= False)

    match_date = models.DateField(db_index=True)

    def __str__(self):
        return str(self.player) + ' ' + str(self.point) + ' ' + str(self.competition) + ' ' + self.result

    class Meta:
        verbose_name= '성적'
        verbose_name_plural= '성적'
        constraints = [
            models.UniqueConstraint(fields=['competition', 'player'], name='unique competition player')
        ]

