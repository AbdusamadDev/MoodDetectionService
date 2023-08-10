# Django
from django.http import JsonResponse, StreamingHttpResponse
from django.db.models import Q
from django.db.models import Avg

# Rest Framework
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.decorators import api_view


# Local applications
from stats.utils import percentage
from stats.pagination import EmployeeStatisticsPagination
from stats.models import Statistics, GeneralStatistics, ExistedStatistics
from stats.serializers import StatisticsSerializer, GeneralStatisticsSerializer
from employees.models import Employee
from employees.serializers import EmployeeSerializer


# Standard packages
from subprocess import check_output
from datetime import datetime
import json
import socket


def home(request):
    return JsonResponse(
        data={"[INFO]": "Web Camera Application started successfully. Status: 200"},
        status=200,
    )


class UserStatisticsListAPIView(ListAPIView):
    model = GeneralStatistics
    serializer_class = GeneralStatisticsSerializer
    lookup_field = "user_id"

    def get_queryset(self):
        query = self.model.objects.filter(user_id=self.kwargs.get("user_id"))
        return query


class EmotionsInPeriodAPIView(APIView):
    def get(self, request, *args, **kwargs):
        year_one = request.query_params.get("year_one")
        month_one = request.query_params.get("month_one")
        week_one = request.query_params.get("week_one")
        day_one = request.query_params.get("day_one")

        year_two = request.query_params.get("year_two")
        month_two = request.query_params.get("month_two")
        week_two = request.query_params.get("week_two")
        day_two = request.query_params.get("day_two")

        user = request.query_params.get("user")

        # Build filter conditions based on user input
        filter_conditions = Q(year__gte=year_one, year__lte=year_two)

        if month_one:
            filter_conditions &= Q(month__gte=month_one)
        if month_two:
            filter_conditions &= Q(month__lte=month_two)

        if week_one:
            filter_conditions &= Q(week__gte=week_one)
        if week_two:
            filter_conditions &= Q(week__lte=week_two)

        if day_one:
            filter_conditions &= Q(day__gte=day_one)
        if day_two:
            filter_conditions &= Q(day__lte=day_two)

        if user:
            filter_conditions &= Q(user_id=user)

        # Filter the records based on the user's input for the period
        queryset = GeneralStatistics.objects.filter(filter_conditions)

        serializer = GeneralStatisticsSerializer(queryset, many=True)
        return Response(serializer.data)

class IntervalStatisticsAPIView(RetrieveAPIView):
    model = GeneralStatistics
    queryset = GeneralStatistics.objects.all()

    def get_queryset(self):
        return self.queryset

    def get(self, request, *args, **kwargs):
        user = request.query_params.get("user")
        year = request.query_params.get("year")
        month = request.query_params.get("month")
        day = request.query_params.get("day")
        query = self.get_queryset()
        if user:
            query = query.filter(user_id=user)
        if year:
            query = query.filter(year=year)
        if month:
            query = query.filter(month=month)
        if day:
            query = query.filter(day=day)
        if not query:
            return Response(data={}, status=200)
        data = query.aggregate(
            sad=Avg("sad"),
            happy=Avg("happy"),
            angry=Avg("angry"),
            neutral=Avg("neutral"),
            surprise=Avg("surprise"),
            disguised=Avg("disguised"),
            anxious=Avg("anxious"),
        )
        return Response(data=percentage(data, user=user))


class StatisticsListAPIView(RetrieveAPIView):
    model = GeneralStatistics
    queryset = GeneralStatistics.objects.all()

    def get_queryset(self):
        return self.model.objects.all()

    def get(self, request, *args, **kwargs):
        user = request.query_params.get("user")
        duration = request.query_params.get("duration")
        query = self.get_queryset()
        if user:
            query = query.filter(user_id=user)
        if duration:
            now = datetime.now()
            if duration == "day":
                query = query.filter(day=now.strftime("%d"))
            elif duration == "week":
                query = query.filter(week=str(now.strftime("%U")))
                print(str(now.strftime("%U")))
                print(query)
            elif duration == "month":
                print(True)
                query = query.filter(month=int(now.strftime("%m")))
            elif query == "year":
                query = query.filter(year=now.strftime("%Y"))
        if query:
            data = query.aggregate(
                sad=Avg("sad"),
                happy=Avg("happy"),
                angry=Avg("angry"),
                neutral=Avg("neutral"),
                surprise=Avg("surprise"),
                disguised=Avg("disguised"),
                anxious=Avg("anxious"),
            )
            return Response(data=percentage(data, user=user))

        return Response(data={}, status=200)


class EmotionStatisticsStreamingAPIView(APIView):
    model = Statistics

    def get(self, request, *args, **kwargs):
        self.model.objects.all().delete()

        def generator():
            while True:
                if len(self.model.objects.all()) > 0:
                    for i in self.model.objects.all():
                        try:
                            context = [
                                {
                                    "camera_url": i.camera_url,
                                    "user_id": i.user_id,
                                    "emotion": {
                                        "neytral": i.neutral,
                                        "xursanchilik": i.happy,
                                        "gamgin": i.sad,
                                        "xavotir": i.anxious,
                                        "jahldorlik": i.angry,
                                        "behuzur": i.disguised,
                                        "hayron": i.surprise,
                                    },
                                }
                            ]
                            yield json.dumps(context)
                            i.delete()
                        except Exception:
                            continue
                    break

        return StreamingHttpResponse(generator(), content_type="application/json")


class EmotionLocalStatisticsStreamingAPIView(APIView):
    model = Statistics

    def get(self, request, *args, **kwargs):
        def generator():
            while True:
                if len(self.model.objects.all()) > 0:
                    for i in self.model.objects.all():
                        try:
                            context = [
                                {
                                    "camera_url": i.camera_url,
                                    "user_id": i.user_id,
                                    "emotion": {
                                        "neytral": i.neutral,
                                        "xursanchilik": i.happy,
                                        "gamgin": i.sad,
                                        "xavotir": i.anxious,
                                        "jahldorlik": i.angry,
                                        "behuzur": i.disguised,
                                        "hayron": i.surprise,
                                    },
                                }
                            ]
                            yield json.dumps(context)
                            i.delete()
                        except Exception:
                            continue
                    break

        return StreamingHttpResponse(generator(), content_type="application/json")


class ExistedStatisticsStreamingAPIView(APIView):
    model = ExistedStatistics

    def get(self, request, *args, **kwargs):
        self.model.objects.all().delete()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        print(ip_address)
        def generator():
            while True:
                if len(self.model.objects.all()) > 0:
                    for i in self.model.objects.all():
                        user = Employee.objects.get(employee_id=i.user_id)
                        context = [
                            {
                                "camera_url": i.camera_url,
                                "user_id": i.user_id,
                                "first_name": user.first_name,
                                "last_name": user.last_name,
                                "middle_name": user.middle_name,
                                "rank": user.rank,
                                "position": user.position,
                                "image": f"http://{ip_address}:16687/media"
                                + str(user.main_image),
                            }
                        ]
                        yield json.dumps(context)
                        i.delete()
                    break

        return StreamingHttpResponse(generator(), content_type="application/json")


class ExistStatisticsStreamingAPIView(APIView):
    model = ExistedStatistics

    def get(self, request, *args, **kwargs):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        def generator():
            while True:
                if len(self.model.objects.all()) > 0:
                    for i in self.model.objects.all():
                        user = Employee.objects.get(employee_id=i.user_id)
                        context = [
                            {
                                "camera_url": i.camera_url,
                                "user_id": i.user_id,
                                "first_name": user.first_name,
                                "last_name": user.last_name,
                                "middle_name": user.middle_name,
                                "rank": user.rank,
                                "position": user.position,
                                "image": f"http://{ip_address}:16687/media"
                                + str(user.main_image),
                            }
                        ]
                        yield json.dumps(context)
                        i.delete()
                    break

        return StreamingHttpResponse(generator(), content_type="application/json")


