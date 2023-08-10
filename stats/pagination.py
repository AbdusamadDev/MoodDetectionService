from rest_framework.pagination import PageNumberPagination


class EmployeeStatisticsPagination(PageNumberPagination):
    page_size = 5  # Number of items to include in each page
    page_size_query_param = "page_size"
    max_page_size = 10
