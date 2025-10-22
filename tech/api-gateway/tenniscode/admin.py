from django.apps import apps
from django.contrib import admin
from django.utils.safestring import mark_safe

import tenniscode.models as tenniscode_models

@admin.register(tenniscode_models.Player)
class PlayerAdmin(admin.ModelAdmin):
    ordering = ['-master_point', '-challenger_point',]
    list_display = ['name', 'rank', 'prev_rank', 'main_club_str', 'clubs_str', 'full_point', 'master_point', 'challenger_point', 'player_level', '기준일', ]
    list_filter = ['기준일', 'player_level', 'main_club_str',]
    search_fields = ['name', 'main_club_str']

@admin.register(tenniscode_models.Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in tenniscode_models.Performance._meta.fields]
    list_filter = ['performance_level', 'is_effective', 'player']
    search_fields = ['result',]

@admin.register(tenniscode_models.Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in tenniscode_models.Competition._meta.fields]
    list_filter = ['category', 'comp_type']
    search_fields = ['title',]

@admin.register(tenniscode_models.Club)
class ClubAdmin(admin.ModelAdmin):
    ordering = ['-full_point',]
    list_display = [
        'title', '기준일',
        'profile',
        'full_point', 'master_point', 'challenger_point',
        'full_rank', 'master_rank', 'challenger_rank',
        'players_count_having_performance',
        'prev_full_rank', 'prev_master_rank', 'prev_challenger_rank',
    ]
    search_fields = ['title',]

    def profile(self, obj):
        html = f"""
            <a href='/adminachy/tenniscode/clubprofile/{obj.clubprofile.id}/' target="_blank">보기</a>
        """
        return mark_safe(html)

@admin.register(tenniscode_models.ClubProfile)
class ClubProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in tenniscode_models.ClubProfile._meta.fields]
    search_fields = ['id',]
    # list_filter = [field.name for field in tenniscode_models.ClubProfile._meta.fields]

@admin.register(tenniscode_models.AnonClubComment)
class AnonClubCommentAdmin(admin.ModelAdmin):
    list_display = ['writer_name', 'club', 'is_deleted', 'content', 'writer_pw', 'writer_ip', 'parent', 'created_at']
    search_fields = ['comment',]


# class ListAdminMixin(object):
#     def __init__(self, model, admin_site):
#         self.list_display = [field.name for field in model._meta.fields]
#         self.search_fields = [field.name for field in model._meta.fields]
#         super(ListAdminMixin, self).__init__(model, admin_site)

# models = apps.get_models()
# for model in models:
#     admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
#     try:
#         admin.site.register(model, admin_class)
#     except admin.sites.AlreadyRegistered:
#         pass

