# import sqlite3
# from datetime import datetime

# class BaseModel(object):
#     """BaseModel that operates in Database"""

#     connection = sqlite3.connect('./db.sqlite3')  # Replace 'my_database.db' with your SQLite DB name.
#     cursor = connection.cursor()

#     def __init__(
#         self,
#         user=None,
#         cam=None,
#         emotion=None,
#         happy=None,
#         angry=None,
#         sad=None,
#         anxious=None,
#         disguised=None,
#         surprise=None,
#         neutral=None,
#     ):
#         self.user = user
#         self.cam = cam
#         self.emotion = emotion
#         self.happy = happy
#         self.angry = angry
#         self.anxious = anxious
#         self.disguised = disguised
#         self.surprise = surprise
#         self.neutral = neutral
#         self.sad = sad

#     def save(self, table_name):
#         now = datetime.now()
#         print("Save in progress...")
#         if table_name == "stats_generalstatistics":
#             self.cursor.execute(
#                 f"""
#                     INSERT INTO {table_name} (
#                         camera_url, 
#                         user_id, 
#                         happy,
#                         angry,
#                         anxious,
#                         disguised,
#                         surprise,
#                         neutral,
#                         sad, 
#                         date_created, 
#                         day, 
#                         week, 
#                         month, 
#                         year
#                     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 """,
#                 (
#                     self.cam,
#                     self.user,
#                     self.happy,
#                     self.angry,
#                     self.anxious,
#                     self.disguised,
#                     self.surprise,
#                     self.neutral,
#                     self.sad,
#                     str(now),
#                     int(now.strftime("%d")),
#                     str(now.strftime("%U")),
#                     str(int(now.strftime("%m"))),
#                     int(now.strftime("%Y")),
#                 ),
#             )
#         elif table_name == "stats_existedstatistics":
#             self.cursor.execute(
#                 f"""
#                     INSERT INTO {table_name} (camera_url, user_id, date_created) VALUES (?, ?, ?)
#                 """,
#                 (
#                     self.cam,
#                     self.user,
#                     str(now)
#                 ),
#             )
#         else:
#             self.cursor.execute(
#                 f"""
#                     INSERT INTO {table_name} (
#                         camera_url, 
#                         user_id, 
#                         happy,
#                         angry,
#                         anxious,
#                         disguised,
#                         surprise,
#                         neutral,
#                         sad, 
#                         date_created
#                     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 """,
#                 (
#                     self.cam,
#                     self.user,
#                     self.happy,
#                     self.angry,
#                     self.anxious,
#                     self.disguised,
#                     self.surprise,
#                     self.neutral,
#                     self.sad,
#                     str(now),
#                 ),
#             )
#         self.connection.commit()

#     def get(self, table_name):
#         self.cursor.execute(
#             f"""
#                 SELECT * FROM {table_name};
#             """
#         )
#         return self.cursor.fetchall()
import sqlite3


def get_details(first_name):
    connection = sqlite3.connect("./db.sqlite3")
    cursor = connection.cursor()
    query = cursor.execute("""SELECT * FROM api_criminals WHERE first_name=?""",
                           (first_name,))
    if query:
        return query.fetchall()[0]
    return []


def get_camera(url):
    connection = sqlite3.connect("./db.sqlite3")
    cursor = connection.cursor()
    query = cursor.execute("""SELECT * FROM api_camera WHERE url=?""", (url,))
    if query:
        return query.fetchall()[0]
    return []