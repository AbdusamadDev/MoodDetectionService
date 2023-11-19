from rest_framework.viewsets import ModelViewSet

from api.models import Employee, Camera
from api.serializers import EmployeeSerializer, CameraSerializer


class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class CameraViewSet(ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
