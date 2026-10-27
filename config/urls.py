"""Root URL configuration; authentication routes are intentionally omitted."""
from django.conf import settings
from django.urls import include, path
from django.views.static import serve as serve_static
from .views import home

urlpatterns = [
    # Local evaluation uses Django's static view so assets also work with DEBUG=False.
    # A production deployment should serve static files through its web server/CDN.
    path("static/<path:path>", serve_static, {"document_root": settings.BASE_DIR / "static"}),
    path("", home, name="home"),
    path("centers/", include("centers.urls")),
    path("", include("players.urls")),
    path("", include("games.urls")),
]

handler404 = "config.views.custom_404"
