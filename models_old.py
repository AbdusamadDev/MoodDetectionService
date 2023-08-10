import psycopg2

from datetime import datetime


class BaseModel(object):
    """BaseModel that operates in Database"""

    connection = psycopg2.connect(
        user="ocean", password="0000", database="postgres", port=5432, host="localhost"
    )
    cursor = connection.cursor()

    def __init__(
        self,
        user=None,
        cam=None,
        emotion=None,
        happy=None,
        angry=None,
        sad=None,
        anxious=None,
        disguised=None,
        surprise=None,
        neutral=None,
    ):
        self.user = user
        self.cam = cam
        self.emotion = emotion
        self.happy = happy
        self.angry = angry
        self.anxious = anxious
        self.disguised = disguised
        self.surprise = surprise
        self.neutral = neutral
        self.sad = sad
        self.connection.commit()

    def save(self, table_name):
        now = datetime.now()
        if table_name == "stats_generalstatistics":
            self.cursor.execute(
                f"""
                    INSERT INTO {table_name} (
                        camera_url, 
                        user_id, 
                        happy,
                        angry,
                        anxious,
                        disguised,
                        surprise,
                        neutral,
                        sad, 
                        date_created, 
                        day, 
                        week, 
                        month, 
                        year
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    self.cam,
                    self.user,
                    self.happy,
                    self.angry,
                    self.anxious,
                    self.disguised,
                    self.surprise,
                    self.neutral,
                    self.sad,
                    str(now),
                    int(now.strftime("%d")),
                    str(now.strftime("%U")),
                    str(int(now.strftime("%m"))),
                    int(now.strftime("%Y")),
                ),
            )
        elif table_name == "stats_existedstatistics":
            self.cursor.execute(
                f"""
                    INSERT INTO {table_name} (camera_url, user_id, date_created) VALUES ('{self.cam}', '{self.user}', '{str(now)}')
                """
            )
        else:
            self.cursor.execute(
                f"""
                    INSERT INTO {table_name} (
                        camera_url, 
                        user_id, 
                        happy,
                        angry,
                        anxious,
                        disguised,
                        surprise,
                        neutral,
                        sad, 
                        date_created
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.cam,
                    self.user,
                    self.happy,
                    self.angry,
                    self.anxious,
                    self.disguised,
                    self.surprise,
                    self.neutral,
                    self.sad,
                    str(now),
                ),
            )
        self.connection.commit()

    def get(self, table_name):
        self.cursor.execute(
            f"""
                SELECT * FROM {table_name};
            """
        )
        rows = self.cursor.fetchall()
        return rows


if __name__ == "__main__":
    print(BaseModel(cam="http://192.168.1.111:22334", user="77777777").get("stats_existedstatistics"))
