from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import threading
from imutils.video import VideoStream
from FaceClass import FaceDetector

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

last_detected_time = time.time()  # Initialize to current time
face_present = False

def start_video_processing():
    global last_detected_time, face_present

    # Initialize video stream
    vs = VideoStream(src="http://192.168.4.49:4747/video").start()
    time.sleep(1.0)  # Allow camera sensor to warm up

    detector = FaceDetector(root_dir='media', model_weights='model.h5')

    # Continuously read frames and process them
    while True:
        frame = vs.read()
        results = detector.detect_faces_from_frame(frame)
        
        # Check if a face is currently detected
        current_face_detected = any([result["user_id"] for result in results])
        
        # Case: A face is detected now, but wasn't detected in previous frames
        if current_face_detected and not face_present:
            for result in results:
                print(result)  # Print result to console
                socketio.emit('frame_data', result, namespace='/')  # Send data to browser

            last_detected_time = time.time()  # Reset the timer after notifying

        # Case: A face was detected previously, but isn't detected now
        elif not current_face_detected and face_present:
            face_present = False
            last_detected_time = time.time()  # Start the timer to keep track of disappearance
        
        # Case: A face reappears after disappearing for at least 3 seconds
        elif current_face_detected and not face_present and (time.time() - last_detected_time >= 3):
            for result in results:
                print(result)  # Print result to console
                socketio.emit('frame_data', result, namespace='/')  # Send data to browser

            last_detected_time = time.time()  # Reset the timer after notifying

        # Update the state
        face_present = current_face_detected

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
