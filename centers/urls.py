from django.urls import path
from . import views

app_name = "centers"
urlpatterns = [
    path("", views.CenterListView.as_view(), name="center_list"),
    path("new/", views.CenterCreateView.as_view(), name="center_create"),
    path("<int:pk>/", views.CenterDetailView.as_view(), name="center_detail"),
    path("<int:pk>/edit/", views.CenterUpdateView.as_view(), name="center_update"),
    path("<int:pk>/delete/", views.CenterDeleteView.as_view(), name="center_delete"),
]
