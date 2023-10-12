from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import threading
from imutils.video import VideoStream
from FaceClass import FaceDetector

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def start_video_processing():
    # Initialize video stream
    vs = VideoStream(src="http://192.168.4.49:4747/video").start()
    time.sleep(1.0)  # Allow camera sensor to warm up

    detector = FaceDetector(root_dir='media', model_weights='model.h5')

    # Continuously read frames and process them
    while True:
        frame = vs.read()
        results = detector.detect_faces_from_frame(frame)
        for result in results:
            print(result)  # Print result to console
            socketio.emit('frame_data', result, namespace='/')  # Send data to browser

    vs.stop()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print("Client connected")

if __name__ == '__main__':
    video_thread = threading.Thread(target=start_video_processing)
    video_thread.start()
    
    # Run Flask app
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False)
