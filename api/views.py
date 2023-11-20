from django.http import StreamingHttpResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView

from api.models import Employee, Camera
from api.serializers import EmployeeSerializer, CameraSerializer

from imutils.video import VideoStream
import cv2
import time


class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class CameraViewSet(ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer


class VideoStreamAPIView(APIView):
    def get(self, request, *args, **kwargs):
        url = request.query_params.get('url')
        if not url:
            return StreamingHttpResponse('URL parameter is missing', status=400, content_type='text/plain')

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

                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       bytearray(encodedImage) + b'\r\n')

        return StreamingHttpResponse(
            frame_generator(),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
