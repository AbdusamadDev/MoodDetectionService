from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("api/", include("api.urls")),
    path("employees/", include("employees.urls")),
    path("admin/", admin.site.urls),
    path("ip/", include("camera.urls")),
    path("stats/", include("stats.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
