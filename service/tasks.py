import asyncio
from imutils.video import VideoStream
from stream import MainStream
from path import absolute_path
from celery import Celery
from celery.schedules import crontab

app = Celery('camera_tasks', broker='redis://localhost:6379/0')
app.conf.beat_schedule = {
    'check_and_connect_cameras': {
        'task': 'myapp.tasks.check_and_connect_cameras',
        'schedule': crontab(minute='*/5'),  # Adjust the interval as needed
    },
}
app.autodiscover_tasks(['tasks'])


@app.task(bind=True, name='camera_tasks.connect_to_camera')
def connect_to_camera(self, url):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        cap = VideoStream(url).start()
        print(f"Camera {url} connected")
        stream_instance = MainStream(absolute_path + "/employees/")
        loop.run_until_complete(stream_instance.continuous_stream_faces(cap, url))
    except Exception as e:
        print(f"Error connecting to camera {url}: {e}")
    finally:
        cap.stop()
        loop.close()
