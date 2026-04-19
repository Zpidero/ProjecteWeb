from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('random-players/', views.get_random_players, name='random_players'),
    path('game/', views.game_view, name='game'),
    path('players/', views.players_list, name='players_list'),
    path('teams/', views.teams_list, name='teams_list'),
    path('player/<int:player_id>/', views.player_detail, name='player_detail'),
    path('teams/<path:team_name>/', views.team_detail, name='team_detail'),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("save-draft/", views.save_draft, name="save_draft"),
    path("my-drafts/", views.my_drafts, name="my_drafts"),
]

