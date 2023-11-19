from django.core.files.storage import FileSystemStorage
from django.contrib.postgres.fields import ArrayField
from django.db import models


def employee_image_path(instance, filename):
    return f'employees/{instance.pk}/main.jpg'


class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    rank = models.CharField(max_length=100)
    bio = models.TextField(max_length=1000)
    image = models.ImageField(upload_to=employee_image_path, null=False)

    def save(self, *args, **kwargs):
        temp_image = self.image
        self.image = None
        super().save(*args, **kwargs)
        self.image = temp_image
        if 'force_insert' in kwargs:
            kwargs.pop('force_insert')
        super().save(*args, **kwargs)
        if self.image:
            storage = FileSystemStorage()
            new_path = employee_image_path(self, self.image.name)
            if not storage.exists(new_path):
                old_path = self.image.name
                self.image.save(new_path, storage.open(old_path))
                storage.delete(old_path)


class Camera(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=150, null=False)
    image = models.ImageField(upload_to='media/cameras/', blank=True)


class FaceEncoding(models.Model):
    # You can add other fields here as needed
    name = models.CharField(max_length=100)
    encoding = ArrayField(
        models.FloatField(),  # Assuming each encoding is a list of floats
        size=128,  # Specify the size if you know the length of the encoding array
    )

    def __str__(self):
        return self.name
