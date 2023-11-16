from rest_framework.viewsets import ModelViewSet

from api.models import Employee
from api.serializers import EmployeeSerializer


class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
