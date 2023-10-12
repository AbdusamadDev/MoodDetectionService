import logging
import time
from collections import Counter, defaultdict
from FaceClass import FaceDetector
from models import BaseModel
import os
import asyncio
import torch
import tensorflow as tf




logging.basicConfig(level=logging.INFO)

ROOT_DIR = "./media"
MODEL_WEIGHTS = "./model.h5"
NO_DATA_LIMIT = 10

class User:
    def __init__(self, id, cam_id, emotion, timestamp):
        self.id = id
        self.cam_id = cam_id
        self.start_time = timestamp
        self.last_seen = timestamp
        self.emotions = [emotion]
        self.five_sec_emotion_printed = False

    def update(self, emotion, timestamp):
        self.last_seen = timestamp
        self.emotions.append(emotion)

def calculate_weighted_emotion(emotions):
    total_emotions = len(emotions)
    emotion_counter = Counter(emotions)
    emotion_percents = {
        emotion: round(count / total_emotions * 100)
        for emotion, count in emotion_counter.items()
    }
    return emotion_percents

async def display_exist(output, user_dict, cam_id):
    user_id = output["user_id"]
    emotion = output["emotion"]
    current_time = time.time()

    if user_id not in user_dict[cam_id]:
        print(f'Exist: {output["user_id"]}')
        user_dict[cam_id][user_id] = User(
            user_id, cam_id, emotion, current_time
        )
    else:
        user_dict[cam_id][user_id].update(emotion, current_time)

async def display_temp(user_dict):
    for cam_id, users in list(user_dict.items()):
        for user_id, user in list(users.items()):
            emotion_result = calculate_weighted_emotion(user.emotions)
            if (
                time.time() - user.start_time > 5
                and not user.five_sec_emotion_printed
                and user_id is not None
            ):
                print(f"Temp: {emotion_result}")
                user.five_sec_emotion_printed = True

async def save_general(user_dict, cam_id, base):
    for cam_id, users in list(user_dict.items()):
        for user_id, user in list(users.items()):
            emotion_result = calculate_weighted_emotion(user.emotions)
            if time.time() - user.last_seen > 1 and user.five_sec_emotion_printed and user_id is not None:
                user = user_dict[cam_id].pop(user_id)
                base.user = user.id
                base.happy = emotion_result.get("xursandchilik", 0)
                base.sad = emotion_result.get("gamgin", 0)
                base.angry = emotion_result.get("jahldorlik", 0)
                base.disguised = emotion_result.get("behuzur", 0)
                base.anxious = emotion_result.get("xavotir", 0)
                base.surprise = emotion_result.get("xayron", 0)
                base.neutral = emotion_result.get("neytral", 0)
                print("General", calculate_weighted_emotion(user.emotions))
                base.save("stats_generalstatistics")

async def handle_camera_ex(idx, video_capture, detector, user_dict, camera_urls):    
    base = BaseModel(cam=camera_urls[idx])
    try:
        output = next(detector.detect_and_display_faces(video_capture))
    except StopIteration:
        logging.info("Выход из цикла while")
        return
    except Exception as e:
        logging.error(f"Ошибка при обработке видеозахвата: {e}")
        return

    cam_id = camera_urls[idx]
    await display_exist(output, user_dict, cam_id)
    await display_temp(user_dict)


async def handle_camera(idx, video_capture, detector, user_dict, camera_urls):    
    base = BaseModel(cam=camera_urls[idx])
    try:
        output = next(detector.detect_and_display_faces(video_capture))
    except StopIteration:
        logging.info("Выход из цикла while")
        return
    except Exception as e:
        logging.error(f"Ошибка при обработке видеозахвата: {e}")
        return

    cam_id = camera_urls[idx]
    await save_general(user_dict, cam_id, base)

async def initialize():
    cam_data = BaseModel()
    camera_urls = ["http://192.168.4.49:4747/video"]
    
    if not os.path.exists(ROOT_DIR):
        os.makedirs(ROOT_DIR)
        
    detector = FaceDetector(ROOT_DIR, MODEL_WEIGHTS)
    
    if camera_urls is not None:
        detector.add_camera(camera_urls)
    
    user_dict = defaultdict(dict)
    detector.load_face_encodings(ROOT_DIR)
    
    return camera_urls, detector, user_dict

async def main():
    camera_urls, detector, user_dict = await initialize()

    while True:
        tasks = [
            handle_camera(idx, video_capture, detector, user_dict, camera_urls)
            for idx, video_capture in enumerate(detector.video_captures)
        ]
        tasks_ex = [
            handle_camera_ex(idx, video_capture, detector, user_dict, camera_urls)
            for idx, video_capture in enumerate(detector.video_captures)
        ]
        await asyncio.gather(*tasks_ex)
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
