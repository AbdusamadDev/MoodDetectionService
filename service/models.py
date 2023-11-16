import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class Database:
    def __init__(self):
        self.dbname = os.environ.get("DATABASE")
        self.user = os.environ.get("USER")
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
            self.cursor = cursor
            cursor.execute(query, params)
            result = cursor.fetchall()
            conn.commit()
            conn.close()
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_details(self, first_name):
        query = "SELECT * FROM api_criminals WHERE id=%s"
        rows = self._execute_query(query, (first_name,))
        return rows[0] if rows else []

    def get_camera(self, url):
        query = "SELECT * FROM api_camera WHERE url=%s"
        rows = self._execute_query(query, (url,))
        return rows[0] if rows else []

    def get_camera_urls(self):
        query = "SELECT url FROM api_camera"
        rows = self._execute_query(query, ())
        return [row[0] for row in rows] if rows else []

    def get_encodings(self):
        query = self._execute_query(
            """SELECT criminal_id, encoding FROM api_encodings;""", ()
        )
        return [row[-1] for row in query], [rower[0] for rower in query]

    def insert_records(self, image, date_recorded, criminal, camera):
        connection = self._db_connect()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO api_criminalsrecords (image_path, date_recorded, criminal_id, camera_id)
            VALUES (%s, %s, %s, %s)
            """,
            (image, date_recorded, criminal, camera)
        )
        connection.commit()

    def get_by_similar(self, partial_url):
        query = """SELECT * FROM api_camera WHERE url ILIKE %s;"""
        connection = self._db_connect()
        cursor = connection.cursor()

        # Add '%' wildcard before and after the partial_url to find similar matches
        like_pattern = f"%{partial_url}%"

        cursor.execute(query, (like_pattern,))
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        keys = ["id", "name", "url", "longitude", "latitude", "image"]
        if results:
            results = results[0]
        context_zip = list(zip(keys, results))
        context = {key: val for key, val in context_zip}

        return context


def get_details(first_name):
    connection = psycopg2.connect(
        dbname="postgres", user="postgres", password="2005", host="localhost"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM api_criminals WHERE first_name=%s", (first_name,))
    query = cursor.fetchall()
    connection.close()
    if query:
        return query[0]
    return []


def get_camera(url):
    connection = psycopg2.connect(
        dbname="postgres", user="postgres", password="2005", host="localhost"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM api_camera WHERE url=%s", (url,))
    query = cursor.fetchall()
    connection.close()
    if query:
        return query[0]
    return []


def get_camera_urls():
    connection = psycopg2.connect(
        dbname="postgres", user="postgres", password="2005", host="localhost"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT url FROM api_camera")
    cameras = cursor.fetchall()
    connection.close()
    return [camera[0] for camera in cameras]


if __name__ == "__main__":
    database = Database()
    print(database.get_by_similar("192.168.1.152"))
