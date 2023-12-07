import time
from datetime import datetime
from utils import save_screenshot, host_address
from models import Database
import json
from firebase_admin import messaging

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
        self.details = {}

    def calculate_mood_percentages(self, mood_list):
        # Initialize a dictionary to hold the sum of normalized values for each mood
        mood_sums = {mood: 0 for mood in mood_list[0].keys()}
        num_frames = len(mood_list)

        # Normalize mood values for each frame and sum them up
        for frame in mood_list:
            frame_total = sum(frame.values())
            for mood, value in frame.items():
                normalized_value = value / frame_total if frame_total != 0 else 0
                mood_sums[mood] += normalized_value

        # Calculate the final mood percentages
        mood_percentages = {mood: round((value / num_frames) * 100, 1) for mood, value in mood_sums.items()}
        return mood_percentages

    async def handle_alert(self, detected_face, mood, url, frame):
        now = time.time()

        # Check if this is a new face or if the face has reappeared after 5 seconds
        last_seen = self.face_last_seen.get(detected_face)
        if last_seen is None or now - last_seen >= 5:
            # New or reappeared face: print identity and reset mood data
            details = self.database.get_details(detected_face)
            camera = self.database.get_camera(url)
            camera["image"] = host_address + "/" + camera.get("image")
            details["image"] = host_address + "/media/" + details.get("image")
            context = {"identity": details, "camera": camera}
            await self.websocket_manager.send_to_all(json.dumps(context))
            print(f"Identity: {details}")
            self.details = context
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
                collected_moods = self.calculate_mood_percentages(self.mood_data[detected_face])
                await self.websocket_manager.send_to_all(
                    json.dumps({**self.details, "mood": collected_moods}))
                year, month, day = datetime.now().timetuple()[:3]
                path = (
                    f"/home/ubuntu/Downloads/MoodDetectionService/media/screenshots/employees/{detected_face}/{year}/{month}/{day}"
                )
                filename = save_screenshot(frame, url, path)[2:]

                camera_object = self.database.get_camera(url)
                if camera_object:
                    camera_object = camera_object.get("id")
                new = ""
                for i in filename.split("/")[4:]:
                    new += "/" + i
                print("Filename euqals to: ", new)
                print("\n\n\n\n\n\n\n\n\n")
                self.database.insert_records(
                    employee=detected_face,
                    camera=camera_object,
                    screenshot=host_address + new,
                    mood=collected_moods
                )

                print(f"Moods for {self.details}: {collected_moods}")
                self.mood_printed[detected_face] = True
                self.mood_data[detected_face] = []
