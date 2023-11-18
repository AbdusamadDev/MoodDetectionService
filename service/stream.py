import torch
import asyncio
import json
import time
import tracemalloc
from datetime import datetime

import websockets
import cv2 
import numpy as np
# from geopy.distance import geodesic
from imutils.video import VideoStream
import os

import tensorflow as tf
from models import Database
from path import absolute_path
from train import FaceTrainer
from utils import save_screenshot, host_address

tracemalloc.start()


# def convert_mood_to_description(mood):
#     mood_descriptions = ["Happy", "Sad", "Angry", "Surprised", "Neutral", "Scared", "Disgusted"]
#     if mood is None:
#         return "Unknown"
#     return mood_descriptions[mood] if 0 <= mood < len(mood_descriptions) else "Unknown"


# Mood Detection Model


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
        self.mood_last_seen = {}
        self.database = Database()

    async def handle_alert(self, detected_face, mood, url):
        now = datetime.now()
        last_alert_time = self.last_alert_time.get(detected_face, datetime.min)
        time_since_last_alert = (now - last_alert_time).total_seconds()

        time_since_last_seen = (now - self.face_last_seen.get(detected_face, datetime.min)).total_seconds()
        if time_since_last_seen > 5 and time_since_last_alert > 3:
            await self.send_alert(detected_face, url, mood)
            self.last_alert_time[detected_face] = now

        self.face_last_seen[detected_face] = now

    async def send_alert(self, detected_face, url, mood):
        details = self.database.get_details(detected_face)
        camera = self.database.get_camera(url)
        camera_details = camera or None
        camera_context = {
            "id": camera_details[0],
            "name": camera_details[1],
            "url": camera_details[2],
            "image": camera_details[-1]
        }
        context = {
            "raw": str(details),
            # "first_name": details[1],
            # "last_name": details[2],
            # "middle_name": details[-1],
            # "age": details[3],
            # "description": details[4],
            # "date_joined": str(details[5]),
            # "image": host_address + "/media/employees/" + str(details[0]) + "/main.jpg",
            # "url": url,
            "camera": camera_context,
            "mood": mood
        }
        await self.websocket_manager.send_to_all(
            json.dumps(context)
        )
        print(context)


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

    async def detect_and_process_faces(self, frame, url):
        self.face_recognition.current_frame = frame
        faces = self.face_model.get(frame)
        tasks = [self.face_recognition.process_face_and_mood(face) for face in faces]
        results = await asyncio.gather(*tasks)
        for name, mood, elapsed_time in results:
            await self.alert_manager.handle_alert(detected_face=name, mood=mood, url=url)

    async def continuous_stream_faces(self, url):
        cap = VideoStream(url).start()
        screenshot_interval = 5  # Interval to take a screenshot in seconds
        last_screenshot_time = time.time()
        try:
            while True:
                frame = cap.read()
                if frame is None:
                    continue

                current_time = time.time()
                if current_time - last_screenshot_time >= screenshot_interval:
                    save_screenshot(frame, path="../media/screenshots/suspends", camera_url=url)
                    last_screenshot_time = current_time

                await self.detect_and_process_faces(frame, url)
        except (KeyboardInterrupt, websockets.exceptions.ConnectionClosedError):
            print("Connection closed")
        finally:
            cap.stop()

    async def multiple_cameras(self):
        while True:
            current_urls = self.database.get_camera_urls()
            if set(current_urls) != set(self.urls):
                self.urls = current_urls
                break

            tasks = [self.continuous_stream_faces(url) for url in self.urls]
            await asyncio.gather(*tasks)
            await asyncio.sleep(5)


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
    image_server = await websockets.serve(image_path_server, "0.0.0.0", 5678)
    ws_server = await websockets.serve(websocket_server, "0.0.0.0", 5000)
    camera_streams = [await stream.continuous_stream_faces(url) for url in stream.urls]
    await asyncio.gather(ws_server, image_server, *camera_streams)


if __name__ == "__main__":
    database = Database()
    camera_urls = database.get_camera_urls()
    stream = MainStream(absolute_path + "/employees/", camera_urls)
    asyncio.run(main())
