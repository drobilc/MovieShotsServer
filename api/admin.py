from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Game)
admin.site.register(Movie)
admin.site.register(Rating)