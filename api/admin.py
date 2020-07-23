from django.contrib import admin
from .models import *

class MovieAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'release_date', 'subtitles_file')

admin.site.register(User)
admin.site.register(Game)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Rating)