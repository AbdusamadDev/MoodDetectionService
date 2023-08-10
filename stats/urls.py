from django.urls import path
from stats import views


urlpatterns = [
    path("list/", views.StatisticsListAPIView.as_view()),
    path("<str:user_id>/details/", views.UserStatisticsListAPIView.as_view()),
    path("exists/", views.ExistedStatisticsStreamingAPIView.as_view()),
    path("stream/", views.EmotionStatisticsStreamingAPIView.as_view()),
    path("emotion/", views.EmotionLocalStatisticsStreamingAPIView.as_view()),
    path("local/", views.ExistStatisticsStreamingAPIView.as_view()),
    path("interval/", views.IntervalStatisticsAPIView.as_view()),
    path("period/", views.EmotionsInPeriodAPIView.as_view()),
]
