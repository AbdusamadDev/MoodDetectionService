from django.urls import path
from employees.views import (
    CreateEmployeeViewSet,
    DeleteEmployeeViewSet,
    ListEmployeeViewSet,
    UpdateEmployeeAPIView,
)


app_name = "employees"

urlpatterns = [
    path(
        "create/",
        CreateEmployeeViewSet.as_view({"get": "list", "post": "create"}),
        name="employee-list",
    ),
    path(
        "<int:pk>/delete/",
        DeleteEmployeeViewSet.as_view(),
        name="employee-detail",
    ),
    path("list/", ListEmployeeViewSet.as_view({"get": "list"})),
    path("<int:pk>/edit/", UpdateEmployeeAPIView.as_view()),
]
