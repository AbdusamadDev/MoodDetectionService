from rest_framework.pagination import PageNumberPagination


class EmployeePagination(PageNumberPagination):
    page_size = 8


class CameraPagination(PageNumberPagination):
    page_size = 8


class RecordsPagination(PageNumberPagination):
    page_size = 4
