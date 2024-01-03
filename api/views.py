from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from api.models import Employee, Camera, Records
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from api.pagination import (
    EmployeePagination,
    RecordsPagination,
    CameraPagination,
)
from api.serializers import (
    EmployeeSerializer,
    RecordsSerializer,
    CameraSerializer,
)
from api.filtersets import (
    EmployeeFilter,
    RecordsFilter,
    CameraFilter,
)

from imutils.video import VideoStream
import time
import cv2


class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all().order_by("-date_recorded")
    serializer_class = EmployeeSerializer
    filterset_class = EmployeeFilter
    pagination_class = EmployeePagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class CameraViewSet(ModelViewSet):
    queryset = Camera.objects.all().order_by("-date_recorded")
    serializer_class = CameraSerializer
    pagination_class = CameraPagination
    filterset_class = CameraFilter
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class RecordsViewSet(ModelViewSet):
    queryset = Records.objects.all().order_by("-date_recorded")
    serializer_class = RecordsSerializer
    pagination_class = RecordsPagination
    filterset_class = RecordsFilter
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class VideoStreamAPIView(APIView):
    def get(self, request, *args, **kwargs):
        url = request.query_params.get("url")
        if not url:
            return StreamingHttpResponse(
                "URL parameter is missing", status=400, content_type="text/plain"
            )

        vs = VideoStream(url).start()
        time.sleep(0.5)  # Warm-up time for the camera

        def frame_generator():
            while True:
                frame = vs.read()
                if frame is None:
                    break

                (flag, encodedImage) = cv2.imencode(".jpg", frame)
                if not flag:
                    continue

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + bytearray(encodedImage)
                    + b"\r\n"
                )

        return StreamingHttpResponse(
            frame_generator(), content_type="multipart/x-mixed-replace; boundary=frame"
        )
