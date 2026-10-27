from django.urls import path
from . import views
app_name = "players"
urlpatterns = [
    path("players/", views.BowlerListView.as_view(), name="bowler_list"),
    path("players/new/", views.BowlerCreateView.as_view(), name="bowler_create"),
    path("players/<int:pk>/", views.BowlerDetailView.as_view(), name="bowler_detail"),
    path("players/<int:pk>/edit/", views.BowlerUpdateView.as_view(), name="bowler_update"),
    path("players/<int:pk>/delete/", views.BowlerDeleteView.as_view(), name="bowler_delete"),
]
