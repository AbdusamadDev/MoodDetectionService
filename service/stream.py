import torch
import asyncio
import json
import time
import tracemalloc
from datetime import datetime

import websockets
import cv2
import numpy as np
import logging
from imutils.video import VideoStream
import os

import tensorflow as tf
from models import Database
from path import abs_path
from train import FaceTrainer
from multiprocessing import Process
from utils import save_screenshot, host_address

tracemalloc.start()
logging.basicConfig(level=logging.DEBUG)


class WebSocketManager:
    def __init__(self):
        self.web_clients = set()
        self.locations = {}

    async def register(self, websocket, data):
        self.web_clients.add(websocket)

    async def unregister(self, websocket):
        self.web_clients.remove(websocket)

    async def send_to_all(self, message):
        for web_client in self.web_clients:
            if web_client.open:
                await web_client.send(message)


class FaceRecognition:
    def __init__(self, main_stream):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.index = main_stream.index
        self.known_face_names = main_stream.known_face_names
        self.face_model = main_stream.face_model
        self.mood_model = self.create_mood_model()
        self.mood_labels = [
            "jahldorlik",
            "behuzur",
            "xavotir",
            "xursandchilik",
            "gamgin",
            "xayron",
            "neytral",
        ]
        self.current_frame = None
        try:
            self.mood_model.load_weights("./model.h5")
        except Exception as e:
            print(f"Не удалось загрузить веса модели: {e}")
            raise

    def create_mood_model(self):
        try:
            gpus = tf.config.experimental.list_physical_devices("GPU")
            if gpus:
                tf.config.experimental.set_visible_devices(gpus[0], "GPU")
                logical_gpus = tf.config.experimental.list_logical_devices("GPU")
                print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
        except RuntimeError as e:
            print(f"Ошибка при настройке GPU: {e}")

        emotion_model = tf.keras.models.Sequential()
        emotion_model.add(
            tf.keras.layers.Conv2D(
                64, (5, 5), activation="relu", input_shape=(48, 48, 1)
            )
        )
        emotion_model.add(
            tf.keras.layers.MaxPooling2D(pool_size=(5, 5), strides=(2, 2))
        )
        emotion_model.add(tf.keras.layers.Conv2D(64, (3, 3), activation="relu"))
        emotion_model.add(tf.keras.layers.Conv2D(64, (3, 3), activation="relu"))
        emotion_model.add(
            tf.keras.layers.AveragePooling2D(pool_size=(3, 3), strides=(2, 2))
        )
        emotion_model.add(tf.keras.layers.Conv2D(128, (3, 3), activation="relu"))
        emotion_model.add(tf.keras.layers.Conv2D(128, (3, 3), activation="relu"))
        emotion_model.add(
            tf.keras.layers.AveragePooling2D(pool_size=(3, 3), strides=(2, 2))
        )
        emotion_model.add(tf.keras.layers.Flatten())
        emotion_model.add(tf.keras.layers.Dense(1024, activation="relu"))
        emotion_model.add(tf.keras.layers.Dropout(0.2))
        emotion_model.add(tf.keras.layers.Dense(1024, activation="relu"))
        emotion_model.add(tf.keras.layers.Dropout(0.2))
        emotion_model.add(tf.keras.layers.Dense(7, activation="softmax"))
        return emotion_model

    async def process_face_and_mood(self, face):
        try:
            box = face['bbox'].astype(int)
            embedding = face['embedding']
            face_image = self.current_frame[box[1]:box[3], box[0]:box[2]]
            if face_image.size == 0:
                return None, None, None

            # Identity Detection
            D, I = self.index.search(embedding.reshape(1, -1), 1)
            if D[0, 0] < 600:
                name = self.known_face_names[I[0, 0]]

                # Mood Detection (only if the face is recognized)
                face_image_resized_mood = cv2.resize(face_image, (48, 48))
                if face_image_resized_mood.shape[2] == 3:
                    face_image_resized_mood = cv2.cvtColor(face_image_resized_mood, cv2.COLOR_RGB2GRAY)
                face_image_normalized_mood = face_image_resized_mood / 255.0
                face_image_reshaped_mood = np.reshape(face_image_normalized_mood, (1, 48, 48, 1))
                mood_probabilities = self.mood_model.predict(face_image_reshaped_mood, verbose=0)[0]
                mood_percentages = {
                    mood: round(float(prob) * 100, 2) for mood, prob in zip(self.mood_labels, mood_probabilities)
                }
                return name, mood_percentages, None
            else:
                return None, None, None

        except Exception as e:
            print(f"Error in processing face: {e}")
            return None, None, None


class AlertManager:
    def __init__(self, websocket_manager):
        self.websocket_manager = websocket_manager
        self.last_alert_time = {}
        self.face_last_seen = {}
        self.mood_data = {}  # Store mood data for a duration
        self.mood_last_updated = {}  # Timestamp of the last mood update
        self.mood_printed = {}  # Track if mood has been printed
        self.database = Database()
        self.identity_printed = {}

    def collect_moods(self, mood_list):
        # Return the collected list of moods
        return mood_list

    async def handle_alert(self, detected_face, mood, url):
        now = time.time()

        # Check if this is a new face or if the face has reappeared after 5 seconds
        last_seen = self.face_last_seen.get(detected_face)
        if last_seen is None or now - last_seen >= 5:
            # New or reappeared face: print identity and reset mood data
            print(f"Identity: {detected_face}")
            await self.websocket_manager.send_to_all(json.dumps({"identity": detected_face}))
            self.mood_data[detected_face] = []
            self.mood_last_updated[detected_face] = now
            self.mood_printed[detected_face] = False

        # Update last seen time
        self.face_last_seen[detected_face] = now

        if mood:
            # Append mood data
            self.mood_data[detected_face].append(mood)

            # Check if 2 seconds have passed since the face was first seen
            if now - self.mood_last_updated[detected_face] >= 2 and not self.mood_printed[detected_face]:
                # Collect and print mood data
                collected_moods = self.collect_moods(self.mood_data[detected_face])
                await self.websocket_manager.send_to_all(
                    json.dumps({"identified": detected_face, "mood": collected_moods}))
                print(f"Moods for {detected_face}: {collected_moods}")

                # Mark the mood as printed and clear the mood data
                self.mood_printed[detected_face] = True
                self.mood_data[detected_face] = []


class MainStream:
    def __init__(self, root_dir, camera_urls):
        self.database = Database()
        self.websocket_manager = WebSocketManager()
        self.urls = camera_urls
        self.trainer = FaceTrainer(root_dir)
        self.index = self.trainer.index
        self.known_face_names = self.trainer.known_face_names
        self.face_model = self.trainer.face_model
        self.alert_manager = AlertManager(self.websocket_manager)
        self.face_recognition = FaceRecognition(self)
        self.processing_queue = asyncio.Queue()  # Queue for processing frames

    async def capture_and_send_frames(self, url):
        """ Captures frames and sends them to the processing queue. """
        cap = VideoStream(url).start()
        while True:
            frame = cap.read()
            if frame is not None:
                await self.processing_queue.put((frame, url))
            await asyncio.sleep(0.1)

    async def process_frames(self):
        """ Processes frames from all cameras. """
        while True:
            frame, url = await self.processing_queue.get()
            self.face_recognition.current_frame = frame
            faces = self.face_model.get(frame)
            tasks = [self.face_recognition.process_face_and_mood(face) for face in faces]
            results = await asyncio.gather(*tasks)
            for name, mood, _ in results:
                if name is not None:
                    await self.alert_manager.handle_alert(name, mood, url)

    async def reload_face_encodings_periodically(self):
        while True:
            print("Reloading face encodings...")
            self.index, self.known_face_names = self.trainer.load_face_encodings(self.trainer.root_dir)
            self.face_recognition.index, self.face_recognition.known_face_names = self.trainer.load_face_encodings(
                self.trainer.root_dir)
            print("Length of face encodings: ", len(self.face_recognition.known_face_names))
            await asyncio.sleep(10)

    async def start_camera_streams(self):
        """Start frame capture tasks for all cameras and the central processing task."""
        tasks = [asyncio.create_task(self.capture_and_send_frames(url)) for url in self.urls]
        tasks.append(asyncio.create_task(self.process_frames()))
        await asyncio.gather(*tasks)


async def websocket_server(websocket, path):
    manager = stream.websocket_manager
    try:
        message = await websocket.recv()
        data = json.loads(message) or None
        await manager.register(websocket, data)

        while True:
            await asyncio.sleep(10)

    except websockets.exceptions.ConnectionClosedError:
        await manager.unregister(websocket)
    except json.JSONDecodeError:
        await manager.unregister(websocket)
    finally:
        await manager.unregister(websocket)


def list_image_paths(directory):
    relative_paths = [os.path.join(directory, f) for f in os.listdir(directory) if
                      os.path.isfile(os.path.join(directory, f))]
    absolute_paths = [path.replace('../', host_address + "/", 1) for path in relative_paths]
    return absolute_paths


async def send_image_paths(websocket, path):  # type: ignore
    sent_image_paths = set()
    connection_time = datetime.now()
    screenshots_dir = "../media/screenshots/suspends/"

    while True:
        current_image_files = set(
            f for f in os.listdir(screenshots_dir) if os.path.isfile(os.path.join(screenshots_dir, f)))
        current_image_paths = {os.path.join(screenshots_dir, f) for f in current_image_files}
        new_paths = current_image_paths - sent_image_paths
        for file_path in new_paths:
            creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if creation_time > connection_time:
                image_name = os.path.basename(file_path)
                camera_url = image_name.split('|')[-1].rstrip('.jpg')
                camera_object = database.get_by_similar(camera_url)
                image_url = file_path.replace('../', host_address + "/", 1)
                camera_object["image"] = host_address + "/media/" + camera_object.get("image")
                message = {"image_path": image_url, "camera_object": camera_object}
                await websocket.send(json.dumps(message))
                sent_image_paths.add(file_path)
        await asyncio.sleep(5)


async def image_path_server(websocket, path):
    consumer_task = asyncio.ensure_future(send_image_paths(websocket, path))
    done, pending = await asyncio.wait([consumer_task], return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()


async def main():
    # Create WebSocket server tasks
    ws_server = await websockets.serve(websocket_server, "0.0.0.0", 5000)
    image_server = await websockets.serve(image_path_server, "0.0.0.0", 5678)

    # Start the camera streams task
    camera_streams_task = asyncio.create_task(stream.start_camera_streams())
    reload_encodings_task = asyncio.create_task(stream.reload_face_encodings_periodically())

    # Gather and run all the tasks
    await asyncio.gather(
        ws_server.wait_closed(),
        image_server.wait_closed(),
        camera_streams_task,
        reload_encodings_task,  # Include the new task here
    )


if __name__ == "__main__":
    # Initialize the database, URLs, and main stream
    database = Database()
    urls = database.get_camera_urls()
    stream = MainStream(abs_path() + "media/employees", urls)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
