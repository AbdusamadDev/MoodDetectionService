from django.db import models


class TestModel(models.Model):
    digit = models.JSONField()
