from django.urls import path
from . import views

urlpatterns = [
    path('movie/trending', views.trending_movies, name='trending_movies'),
]