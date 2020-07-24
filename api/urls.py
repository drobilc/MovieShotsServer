from django.urls import path
from . import views

urlpatterns = [
    path('game', views.generate_game, name='generate_game'),
    path('game/rate', views.rate_game, name='rate_game'),
    path('suggestions', views.suggestions, name='suggestions'),
    path('movie/trending', views.trending_movies, name='trending_movies'),
    path('game/<int:game_id>/', views.game_details, name='game_details')
]