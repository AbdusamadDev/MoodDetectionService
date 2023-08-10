from rest_framework import serializers
from stats.models import GeneralStatistics, Statistics

from employees.models import Employee


class StatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = "__all__"


class GeneralStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralStatistics
        fields = "__all__"


class StatsEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "last_name",
            "first_name",
            "middle_name",
            "rank",
            "position",
        ]
