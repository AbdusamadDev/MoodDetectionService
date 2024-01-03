import torch
import tensorflow as tf
import cv2
import numpy as np


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
            self.mood_model.load_weights("/home/ubuntu/Downloads/MoodDetectionService/service/model.h5")
        except Exception as e:
            print(f"Unable to load models: {e}")
            raise

    def create_mood_model(self):
        try:
            gpus = tf.config.experimental.list_physical_devices("GPU")
            if gpus:
                tf.config.experimental.set_visible_devices(gpus[0], "GPU")
                logical_gpus = tf.config.experimental.list_logical_devices("GPU")
                print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
        except RuntimeError as e:
            print(f"Failed to set up GPU: {e}")

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
            if D[0, 0] < 500:
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
