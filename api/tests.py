import requests
import sqlite3
import random
import string
import time

def generate():
    alphabet = "abcdefghijklmnopqrstuvxyz"
    return ''.join(random.choice(alphabet) for i in range(13))

def create_mood(conn):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO api_mood (jahldorlik, behuzur, xavotir, hursandchilik, gamgin, xayron, neytral) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (generate(), generate(), generate(), generate(), generate(), generate(), generate())
    )
    conn.commit()
    time.sleep(0.1)
    cursor.execute("SELECT last_insert_rowid()")
    mood_id = cursor.fetchone()[0]
    cursor.close()
    return mood_id

def create_record(conn, screenshot_url, date_recorded, camera_id, employee_id, mood_id):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO api_records (screenshot, date_recorded, camera_id, employee_id, mood_id) VALUES (?, ?, ?, ?, ?)""",
        (screenshot_url, date_recorded, camera_id, employee_id, mood_id)
    )
    conn.commit()
    cursor.close()

def main():
    conn = sqlite3.connect("../db.sqlite3")
    try:
        for i in range(100):
            mood_id = create_mood(conn)
            create_record(
                conn,
                "https://youtube.com/media/main.jpg",
                generate(),
                2,
                1,
                mood_id
            )
    finally:
        conn.close()

if __name__ == "__main__":
    main()
