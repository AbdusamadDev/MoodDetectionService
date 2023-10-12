import os
import datetime
import cv2
import numpy as np
import torch
import tensorflow as tf
import insightface
import faiss

import threading
from imutils.video import VideoStream

tf.config.set_visible_devices([], 'GPU')
torch.backends.cudnn.enabled = False
class FaceDetector:
    def __init__(self, root_dir, model_weights):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        try:
            self.face_model = insightface.app.FaceAnalysis()
            ctx_id = 0
            self.face_model.prepare(ctx_id=ctx_id)
        except Exception as e:
            print(f"Ошибка при инициализации моделей: {e}")
            raise

        self.emotion_labels = [
            "jahldorlik",
            "behuzur",
            "xavotir",
            "xursandchilik",
            "gamgin",
            "xayron",
            "neytral",
        ]
        self.emotion_model = self.create_emotion_model()
        try:
            self.emotion_model.load_weights(model_weights)
        except Exception as e:
            print(f"Не удалось загрузить веса модели: {e}")
            raise

        try:
            self.index, self.known_face_names = self.load_face_encodings(
                root_dir
            )
        except Exception as e:
            print(f"Ошибка при загрузке кодировок лиц: {e}")
            raise

        self.emotion = ""
        self.user_id = ""
        self.video_captures = []
    def create_emotion_model(self):
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

    def load_face_encodings(self, root_dir):
        known_face_encodings = []
        known_face_names = []
        if "media" not in os.listdir(os.getcwd()):
            os.makedirs("media")
        for dir_name in os.listdir(root_dir):
            dir_path = os.path.join(root_dir, dir_name)
            if os.path.isdir(dir_path):
                for file_name in os.listdir(dir_path):
                    if file_name.endswith(".jpg") or file_name.endswith(".png"):
                        image_path = os.path.join(dir_path, file_name)
                        try:
                            image = cv2.imread(image_path)
                            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                            faces = self.face_model.get(image)
                        except Exception as e:
                            print(f"Unable to process image {image_path}: {e}")
                            continue 

                        if faces:
                            face = faces[0]
                            box = face.bbox.astype(int)
                            face_image = image[box[1]:box[3], box[0]:box[2]]
                            if face_image.size == 0:
                                continue
                            face_image = cv2.resize(face_image, (640, 480))
                            face_image = face_image / 255.0
                            face_image = (
                                torch.tensor(face_image.transpose((2, 0, 1)))
                                .float()
                                .to(self.device)
                                .unsqueeze(0)
                            )
                            embedding = face.embedding 
                            known_face_encodings.append(embedding)
                            known_face_names.append(dir_name)
                            
        known_face_encodings = np.array(known_face_encodings)
        index = faiss.IndexFlatL2(known_face_encodings.shape[1])
        index.add(known_face_encodings)

        return index, known_face_names


    def detect_faces_from_frame(self, frame):
        try:
            faces = self.face_model.get(frame)
            if faces is None:
                print("Model could not process frame")
                return
        except Exception as e:
            print(f"Error in face recognition: {e}")
            return

        results = []

        if faces:
            for face in faces:
                box = face.bbox.astype(int)
                face_image = frame[box[1]:box[3], box[0]:box[2]]
                if face_image.size == 0:
                    continue
                face_image = cv2.resize(face_image, (640, 480))
                face_image = face_image / 255.0
                face_image = (
                    torch.tensor(face_image.transpose((2, 0, 1)))
                    .float()
                    .to(self.device)
                    .unsqueeze(0)
                )
                embedding = face.embedding  
                D, I = self.index.search(embedding.reshape(1, -1), 1)                
                if D[0, 0] < 600:
                    name = self.known_face_names[I[0, 0]]
                else:
                    name = False

                face_gray = cv2.cvtColor(
                    frame[box[1] : box[3], box[0] : box[2]], cv2.COLOR_BGR2GRAY
                )
                face_gray = cv2.resize(face_gray, (48, 48))
                face_gray = face_gray / 255.0
                face_gray = np.reshape(face_gray, (1, 48, 48, 1))
                emotion = self.emotion_labels[
                    np.argmax(self.emotion_model.predict(face_gray, verbose=0))
                ]
                results.append({
                    "time": str(datetime.datetime.now()).split(".")[0],
                    "user_id": name,
                    "emotion": emotion,
                })
        else:
            results.append({
                "time": str(datetime.datetime.now()).split(".")[0],
                "user_id": False,
                "emotion": None,
            })

        return results