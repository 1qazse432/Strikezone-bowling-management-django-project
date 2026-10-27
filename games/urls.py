from django.urls import path
from . import views
from centers import views as center_views
app_name = "games"
urlpatterns = [
    path("lanes/", center_views.LaneListView.as_view(), name="lane_list"),
    path("lanes/new/", center_views.LaneCreateView.as_view(), name="lane_create"),
    path("lanes/<int:pk>/", center_views.LaneDetailView.as_view(), name="lane_detail"),
    path("lanes/<int:pk>/edit/", center_views.LaneUpdateView.as_view(), name="lane_update"),
    path("lanes/<int:pk>/delete/", center_views.LaneDeleteView.as_view(), name="lane_delete"),
    path("games/", views.GameListView.as_view(), name="game_list"),
    path("games/new/", views.GameCreateView.as_view(), name="game_create"),
    path("games/<int:pk>/", views.GameDetailView.as_view(), name="game_detail"),
    path("games/<int:pk>/edit/", views.GameUpdateView.as_view(), name="game_update"),
    path("games/<int:pk>/delete/", views.GameDeleteView.as_view(), name="game_delete"),
    path("scores/", views.GameScoreListView.as_view(), name="score_list"),
    path("scores/new/", views.GameScoreCreateView.as_view(), name="score_create"),
    path("games/<int:game_pk>/scores/new/", views.GameScoreCreateView.as_view(), name="score_create_for_game"),
    path("scores/<int:pk>/edit/", views.GameScoreUpdateView.as_view(), name="score_update"),
    path("scores/<int:pk>/delete/", views.GameScoreDeleteView.as_view(), name="score_delete"),
]
