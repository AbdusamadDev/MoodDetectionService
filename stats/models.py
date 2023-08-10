from django.db import models


class Statistics(models.Model):
    user_id = models.CharField(max_length=70)
    camera_url = models.CharField(max_length=120)
    happy = models.IntegerField()
    sad = models.IntegerField()
    angry = models.IntegerField()
    neutral = models.IntegerField()
    anxious = models.IntegerField()
    surprise = models.IntegerField()
    disguised = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)


class GeneralStatistics(models.Model):
    user_id = models.CharField(max_length=70)
    camera_url = models.CharField(max_length=100)
    happy = models.IntegerField()
    sad = models.IntegerField()
    angry = models.IntegerField()
    neutral = models.IntegerField()
    anxious = models.IntegerField()
    surprise = models.IntegerField()
    disguised = models.IntegerField()
    day = models.IntegerField()
    week = models.CharField(max_length=50)
    month = models.CharField(max_length=50)
    year = models.CharField(max_length=10)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "user_id",
                    "happy",
                    "sad",
                    "angry",
                    "disguised",
                    "anxious",
                    "surprise",
                    "neutral",
                    "day",
                    "week",
                    "month",
                    "year"
                ],
                name="indexes"
            )
        ]
    
    def __str__(self) -> str:
        return "User %s Day %s | Week %s | Month %s | Year %s |" % (self.user_id, self.day, self.week, self.month, self.year)


class ExistedStatistics(models.Model):
    user_id = models.CharField(max_length=50)
    camera_url = models.URLField()
    date_created = models.DateTimeField(auto_now_add=True)
