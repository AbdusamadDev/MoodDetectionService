from rest_framework.generics import (
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse
from rest_framework.response import Response

from camera.models import IPAddressModel
from camera.serializers import IPAddressSerializer

import cv2


class IPAddressCreationAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    model = IPAddressModel
    serializer_class = IPAddressSerializer
    queryset = IPAddressModel.objects.all()


class IPAddressUpdateAPIView(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    model = IPAddressModel
    serializer_class = IPAddressSerializer
    queryset = IPAddressModel.objects.all()
    lookup_field = "name"


class IPAddressListAPIView(ListAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]
    model = IPAddressModel
    serializer_class = IPAddressSerializer
    queryset = IPAddressModel.objects.all()


class IPAddressDeleteAPIView(DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    model = IPAddressModel
    serializer_class = IPAddressSerializer
    queryset = IPAddressModel.objects.all()
    lookup_field = "name"

    def delete(self, request, name, format=None):

        ip_obj = get_object_or_404(self.model, name=name)
        ip_obj.delete()
        return JsonResponse({"message": "IP address deleted successfully."})


class CameraSreamingAPIView(RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        camera_url = request.query_params.get("camera", 0)
        capture = cv2.VideoCapture(camera_url)

        def generate_frames():
            while True:
                success, frame = capture.read()
                
                if not success:
                    break
                else:
                    ret, buffer = cv2.imencode(".jpg", frame)
                    frame = buffer.tobytes()
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                    )  # генератор кадров для HTTP потока

        return StreamingHttpResponse(
            generate_frames(), content_type="multipart/x-mixed-replace; boundary=frame"
        )
