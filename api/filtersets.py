import django_filters
from django.db.models import Q
from api.models import Employee, Camera, Records


class EmployeeFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Employee
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(middle_name__icontains=value) |
            Q(position__icontains=value) |
            Q(rank__icontains=value) |
            Q(bio__icontains=value) |
            Q(age__icontains=value)
        )

    first_name = django_filters.CharFilter(lookup_expr='iexact')
    first_name_contains = django_filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='iexact')
    last_name_contains = django_filters.CharFilter(field_name='last_name', lookup_expr='icontains')
    middle_name = django_filters.CharFilter(lookup_expr='iexact')
    middle_name_contains = django_filters.CharFilter(field_name='middle_name', lookup_expr='icontains')
    position = django_filters.CharFilter(lookup_expr='iexact')
    position_contains = django_filters.CharFilter(field_name='position', lookup_expr='icontains')
    rank = django_filters.CharFilter(lookup_expr='iexact')
    rank_contains = django_filters.CharFilter(field_name='rank', lookup_expr='icontains')
    bio_contains = django_filters.CharFilter(field_name='bio', lookup_expr='icontains')


class CameraFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Camera
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(url__icontains=value) |
            Q(image__icontains=value)
        )

    name = django_filters.CharFilter(lookup_expr='iexact')
    name_contains = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    url = django_filters.CharFilter(lookup_expr='iexact')
    url_contains = django_filters.CharFilter(field_name='url', lookup_expr='icontains')


class RecordsFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Records
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(employee__first_name__icontains=value) |
            Q(employee__last_name__icontains=value) |
            Q(employee__middle_name__icontains=value) |
            Q(employee__bio__icontains=value) |
            Q(employee__age__icontains=value) |
            Q(employee__rank__icontains=value) |
            Q(camera__name__icontains=value) |
            Q(camera__url__icontains=value) |
            Q(camera__image__icontains=value) |
            Q(date_recorded__icontains=value) |
            Q(mood__jahldorlik__icontains=value) |
            Q(mood__behuzur__icontains=value) |
            Q(mood__xavotir__icontains=value) |
            Q(mood__hursandchilik__icontains=value) |
            Q(mood__gamgin__icontains=value) |
            Q(mood__xayron__icontains=value) |
            Q(mood__neytral__icontains=value)
        )

    employee = django_filters.NumberFilter()
    camera = django_filters.NumberFilter()
    mood = django_filters.NumberFilter()
    screenshot = django_filters.CharFilter(lookup_expr='iexact')
    screenshot_contains = django_filters.CharFilter(field_name='screenshot', lookup_expr='icontains')
    date_recorded_gte = django_filters.DateTimeFilter(field_name='date_recorded', lookup_expr='gte')
    date_recorded_lte = django_filters.DateTimeFilter(field_name='date_recorded', lookup_expr='lte')
