import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class Database:
    def __init__(self):
        self.dbname = os.environ.get("DATABASE")
        self.user = os.environ.get(
            "DB_USER")  # Changed from "USER" to "DB_USER" to avoid conflict with system variables
        self.password = os.environ.get("PASSWORD")
        self.host = os.environ.get("HOST")
        self.port = os.environ.get("PORT")

    def _db_connect(self):
        return psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

    def _execute_query(self, query, params):
        try:
            conn = self._db_connect()
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            conn.commit()
            cursor.close()  # Moved cursor close here
            conn.close()
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_details(self, employee_id):
        query = "SELECT * FROM api_employee WHERE id=%s"
        rows = self._execute_query(query, (employee_id,))  # Changed parameter name to 'employee_id' for clarity
        labels = ["id", "first_name", "last_name", "middle_name", "position", "rank", "bio", "image", "age"]
        if rows is not None:
            rows_dict = {label: row for label, row in zip(labels, rows[0])}
            return rows_dict
        return None

    def get_camera(self, url):
        query = "SELECT * FROM api_camera WHERE url=%s"
        rows = self._execute_query(query, (url,))
        labels = ["id", "name", "url", "image"]
        if rows is not None:
            rows_dict = {label: row for label, row in zip(labels, rows[0])}
            return rows_dict
        return None

    def get_camera_urls(self):
        query = "SELECT url FROM api_camera"
        rows = self._execute_query(query, ())
        return [row[0] for row in rows] if rows else []

    def get_by_similar(self, partial_url):
        query = """SELECT * FROM api_camera WHERE url ILIKE %s;"""
        rows = self._execute_query(query, (f"%{partial_url}%",))  # Simplified the like_pattern logic
        return rows[0] if rows else None  # Same change as in get_details and get_camera

    def insert_records(self, employee, camera, screenshot, mood):
        connection = self._db_connect()
        cursor = connection.cursor()
        query = '''
        INSERT INTO api_mood (jahldorlik, behuzur, xavotir, hursandchilik, gamgin, xayron, neytral)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        '''
        cursor.execute(query, tuple(i for i in mood.values()))
        mood_id = cursor.fetchone()[0]
        date_recorded = str(datetime.now())
        cursor.execute(
            """
            INSERT INTO api_records 
            (employee_id, camera_id, screenshot, mood_id, date_recorded) VALUES (%s, %s, %s, %s, %s);
            """,
            (employee, camera, screenshot, mood_id, date_recorded)
        )
        connection.commit()


if __name__ == "__main__":
    database = Database()
    mood = {'jahldorlik': 0.2, 'behuzur': 0.0, 'xavotir': 35.3, 'xursandchilik': 0.0, 'gamgin': 14.61, 'xayron': 0.0,
            'neytral': 49.88}
    print(database.insert_records("36", "9", "qweqwe.com", mood))
