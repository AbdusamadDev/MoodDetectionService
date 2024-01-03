from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings

from api.views import (
    EmployeeViewSet,
    CameraViewSet,
    VideoStreamAPIView,
    RecordsViewSet,
)

router = DefaultRouter()
router.register(r"employees", EmployeeViewSet)
router.register(r"cameras", CameraViewSet)
router.register(r"records", RecordsViewSet)
urlpatterns = [
    path("api/", include(router.urls)),
    path("api/stream/", VideoStreamAPIView.as_view(), name="stream"),
    path("auth/token/", obtain_auth_token),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
