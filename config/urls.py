from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from api.views import EmployeeViewSet, CameraViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'cameras', CameraViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
