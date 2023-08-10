from django.urls import path

from api.views import LogoutView, TokenAPIView


urlpatterns = [
    path("login/", TokenAPIView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
