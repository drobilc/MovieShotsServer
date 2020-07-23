from django.contrib import admin
from .models import *

class MovieAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'release_date', 'subtitles_file')
    list_display_links = ('title', )

class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'number_of_players', 'intoxication_level', 'movie')
    list_display_links = ('id', )

class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'game', 'rating')
    list_display_links = ('id', )

admin.site.register(User)
admin.site.register(Game, GameAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Rating, RatingAdmin)