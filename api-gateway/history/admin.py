from django.contrib import admin
import history.models as history_models

@admin.register(history_models.ClubHistory)
class ClubHistoryAdmin(admin.ModelAdmin):
    ordering = ['-full_point',]
    list_display = [
        'title', '기준일',
        'full_point', 'master_point', 'challenger_point',
        'full_rank', 'master_rank', 'challenger_rank',
    ]
    list_filter = ['기준일str',]
    search_fields = ['title',]

@admin.register(history_models.ClubPrepared)
class ClubPreparedAdmin(admin.ModelAdmin):
    ordering = ['-full_point',]
    list_display = [
        'title', '기준일', 'created_at', 'updated_at',
        'full_point', 'master_point', 'challenger_point',
        'full_rank', 'master_rank', 'challenger_rank',
    ]
    search_fields = ['title',]

@admin.register(history_models.PlayerHistory)
class PlayerHistoryAdmin(admin.ModelAdmin):
    ordering = ['-master_point', '-challenger_point',]
    list_display = ['기준일', 'name', 'rank', 'main_club_str', 'full_point', 'master_point', 'challenger_point', 'player_level',]
    list_filter = ['기준일str', 'player_level', 'main_club_str',]
    search_fields = ['name', 'main_club_str']

@admin.register(history_models.PlayerPrepared)
class PlayerPreparedAdmin(admin.ModelAdmin):
    ordering = ['-master_point', '-challenger_point',]
    list_display = ['기준일', 'name', 'rank', 'main_club_str', 'full_point', 'master_point', 'challenger_point', 'player_level',]
    list_filter = ['기준일', 'player_level', 'main_club_str',]
    search_fields = ['name', 'main_club_str']
