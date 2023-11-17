import cv2
import numpy as np
from insightface.app import FaceAnalysis

import tensorflow as tf

print(tf.__version__)
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        # Currently, memory growth needs to be the same across GPUs
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        # Memory growth must be set before GPUs have been initialized
        print(e)


def create_mood_model(num_classes=7):
    from tensorflow.keras.applications import VGG16
    from tensorflow.keras.layers import Dense, Flatten, Dropout
    from tensorflow.keras.models import Model

    base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    for layer in base_model.layers:
        layer.trainable = False

    x = base_model.output
    x = Flatten()(x)
    x = Dense(1024, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def detect_mood(image_path):
    # Load mood model
    mood_model = create_mood_model()

    # Load face detection model
    app = FaceAnalysis()
    app.prepare(ctx_id=0, det_size=(640, 640))

    # Read and process the image
    img = cv2.imread(image_path)
    faces = app.get(img)

    for idx, face in enumerate(faces):
        # Extract and preprocess face image
        bbox = face['bbox'].astype(int)
        x1, y1, x2, y2 = bbox
        face_img = img[y1:y2, x1:x2]
        face_img = cv2.resize(face_img, (224, 224))
        face_img = np.expand_dims(face_img, axis=0)

        # Predict mood
        mood_prediction = mood_model.predict(face_img)
        mood = np.argmax(mood_prediction)
        mood_labels = ["Happy", "Sad", "Angry", "Surprised", "Neutral", "Scared", "Disgusted"]
        mood_text = mood_labels[mood] if mood < len(mood_labels) else "Unknown"

        # Print result
        return f"Face {idx + 1}: {mood_text}"


# Example usage
print(detect_mood("./image.jpg"))
