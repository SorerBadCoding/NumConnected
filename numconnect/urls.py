"""
URL configuration for the NUM Connect project.

Each feature lives in its own app with its own namespaced urls.py, included
here under a clear top-level path. Namespacing keeps `{% url %}` lookups
unambiguous as the project grows (e.g. `assignments:list` vs `events:list`).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("dashboard.urls")),
    path("accounts/", include("accounts.urls")),
    path("assignments/", include("assignments.urls")),
    path("announcements/", include("announcements.urls")),
    path("events/", include("events.urls")),
    path("resources/", include("resources_app.urls")),
    path("ai-assistant/", include("ai_assistant.urls")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
