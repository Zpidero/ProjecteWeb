from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('random-players/', views.get_random_players, name='random_players'),
    path('game/', views.game_view, name='game'),
]