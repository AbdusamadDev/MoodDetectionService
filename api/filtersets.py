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


import django_filters
from django.db.models import Q
from .models import Records  # Ensure this is your actual model import

class RecordsFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    date_recorded_year__gte = django_filters.NumberFilter(field_name='date_recorded', lookup_expr='year__gte')
    date_recorded_year__lte = django_filters.NumberFilter(field_name='date_recorded', lookup_expr='year__lte')
    date_recorded_month__gte = django_filters.NumberFilter(field_name='date_recorded', lookup_expr='month__gte')
    date_recorded_month__lte = django_filters.NumberFilter(field_name='date_recorded', lookup_expr='month__lte')
    date_recorded_day__gte = django_filters.NumberFilter(field_name='date_recorded', lookup_expr='day__gte')
    date_recorded_day__lte = django_filters.NumberFilter(field_name='date_recorded', lookup_expr='day__lte')
    date_recorded_hour__gte = django_filters.NumberFilter(field_name='date_recorded', lookup_expr='hour__gte')
    date_recorded_hour__lte = django_filters.NumberFilter(field_name='date_recorded', lookup_expr='hour__lte')


    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(employee__first_name__icontains=value) |
            Q(employee__last_name__icontains=value) |
            Q(employee__middle_name__icontains=value) |
            Q(employee__bio__icontains=value) |
            Q(employee__rank__icontains=value) |
            Q(camera__name__icontains=value) |
            Q(camera__url__icontains=value) |
            Q(camera__image__icontains=value) |
            Q(mood__jahldorlik__icontains=value) |
            Q(mood__behuzur__icontains=value) |
            Q(mood__xavotir__icontains=value) |
            Q(mood__hursandchilik__icontains=value) |
            Q(mood__gamgin__icontains=value) |
            Q(mood__xayron__icontains=value) |
            Q(mood__neytral__icontains=value)
        )

    class Meta:
        model = Records
        fields = {
            'date_recorded': ['exact', 'year', 'month', 'day', 'hour', 'minute', 'second', 'gte', 'lte'],
            'employee__first_name': ['exact', 'icontains'],
            'employee__middle_name': ['exact', 'icontains'],
            'employee__bio': ['exact', 'icontains'],
            'employee__rank': ['exact', 'icontains'],
            'employee__position': ['exact', 'icontains'],
            'employee__last_name': ['exact', 'icontains'],
            'employee__age': ['exact', 'gte', 'lte'],
            'camera__url': ['exact', 'icontains'],
            'camera__date_recorded': ['exact', 'icontains'],
            "mood__jahldorlik": ["exact", "icontains"],
            "mood__behuzur": ["exact", "icontains"],
            "mood__xavotir": ["exact", "icontains"],
            "mood__gamgin": ["exact", "icontains"],
            "mood__xayron": ["exact", "icontains"],
            "mood__neytral": ["exact", "icontains"],
            "mood__hursandchilik": ["exact", "icontains"],

        }
