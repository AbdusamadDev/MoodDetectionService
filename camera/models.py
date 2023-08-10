from django.db import models


# Create your models here.
class IPAddressModel(models.Model):
    name = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=200, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s " % self.address
