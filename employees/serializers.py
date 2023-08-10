from rest_framework import serializers
from django.core.exceptions import ValidationError
import os

from employees.models import Employee


ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif"]
ALLOWED_ARCHIVE_EXTENSIONS = [".zip"]


class EmployeeSerializer(serializers.Serializer):
    images = serializers.FileField(required=False)
    main_image = serializers.ImageField(required=True)
    first_name = serializers.CharField(required=True)
    employee_id = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    middle_name = serializers.CharField(required=True)
    rank = serializers.CharField(required=True)
    position = serializers.CharField(required=True)

    # class Meta:
    #     model = Employee
    #     fields = '__all__'

    def validate_images(self, value):
        if value.content_type not in [
            "image/jpg",
            "image/jpeg",
            "image/png",
            "image/gif",
            "application/zip",
        ]:
            raise ValidationError("Only images and .zip files are allowed.")

        # Check for image extensions if it's an image file
        if value.content_type in ["image/jpg", "image/jpeg", "image/png", "image/gif"]:
            filename, ext = os.path.splitext(value.name)
            if ext.lower() not in ALLOWED_IMAGE_EXTENSIONS:
                raise ValidationError("Unsupported image file format.")

        return value

    def save(self, **kwargs):
        model = Employee(
            employee_id=self.validated_data["employee_id"],
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
            middle_name=self.validated_data["middle_name"],
            rank=self.validated_data["rank"],
            position=self.validated_data["position"],
            main_image=f"/{self.validated_data['employee_id']}/main.jpg",
            images=self.validated_data["employee_id"],
        )
        model.save()
