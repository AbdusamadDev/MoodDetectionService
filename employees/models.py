from django.db import models


class Employee(models.Model):
    employee_id = models.CharField(max_length=20, unique=True)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    rank = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    main_image = models.ImageField(upload_to="employee_images/", blank=True, null=True)
    images = models.FileField(upload_to="zip_folders/", blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.last_name}, {self.first_name} {self.middle_name or ''}"
