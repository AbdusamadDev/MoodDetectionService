from django.urls import path

from camera import views

urlpatterns = [
    path("create/", views.IPAddressCreationAPIView.as_view()),
    path("<str:name>/update/", views.IPAddressUpdateAPIView.as_view()),
    path("<str:name>/delete/", views.IPAddressDeleteAPIView.as_view()),
    path("list/", views.IPAddressListAPIView.as_view()),
    path("stream/", views.CameraSreamingAPIView.as_view())
]
