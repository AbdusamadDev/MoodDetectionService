# Standard Packages
import os
import shutil
import zipfile

# Django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError

# Rest Framework
from rest_framework import status, viewsets
from rest_framework.generics import DestroyAPIView, UpdateAPIView
from rest_framework.response import Response

# local applications
from employees.models import Employee
from employees.serializers import EmployeeSerializer


ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]


def is_valid_image_extension(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


class CreateEmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def create(self, request, *args, **kwargs):
        shutil.rmtree("media/employee_images", ignore_errors=True)
        shutil.rmtree("media/zip_folders", ignore_errors=True)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        idd = serializer.validated_data.get("employee_id")  # type: ignore
        path = f"media/{idd}"
        main_image_path = os.path.join(path, "main.jpg")

        images = request.FILES.get("images")
        main_image = request.FILES.get("main_image")

        if not images and not main_image:
            raise ValidationError("You must provide either 'images' or 'main_image'.")

        if images:
            if not zipfile.is_zipfile(images):
                raise ValidationError(
                    "If 'images' are provided, it must be a valid ZIP archive."
                )

            zip_file_path = os.path.join(settings.MEDIA_ROOT, f"{idd}.zip")
            with open(zip_file_path, "wb+") as destination:
                for chunk in images.chunks():
                    destination.write(chunk)

            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                image_files = [
                    file
                    for file in zip_ref.namelist()
                    if not file.endswith("/") and is_valid_image_extension(file)
                ]
                if not image_files:
                    raise ValidationError(
                        "The ZIP archive must contain valid image files."
                    )

                for file in image_files:
                    zip_ref.extract(file, path)
                    index = zip_ref.namelist().index(file)
                    new_file_path = os.path.join(path, f"{index + 1}.jpg")
                    os.rename(os.path.join(path, file), new_file_path)

            os.remove(zip_file_path)
            shutil.rmtree("media/employee_images", ignore_errors=True)
            shutil.rmtree("media/zip_folders", ignore_errors=True)

        if main_image:
            # Создаем папку, если её нет
            os.makedirs(path, exist_ok=True)

            with open(main_image_path, "wb+") as destination:
                for chunk in main_image.chunks():
                    destination.write(chunk)

        # serializer.validated_data["main_image"] = f"{idd}/main.jpg"
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ListEmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class DeleteEmployeeViewSet(DestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = "employee_id"

    def get_object(self):
        queryset = self.get_queryset()
        employee_id = self.kwargs["employee_id"]
        obj = queryset.filter(employee_id=employee_id).first()
        self.check_object_permissions(self.request, obj)
        return obj

    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs.get("employee_id")
        if "media" in os.listdir(os.getcwd()):
            try:
                user_id = self.queryset.get(employee_id=pk).employee_id
            except ObjectDoesNotExist:
                return Response(data={"User does not exist"})
            for folder in os.listdir("media/"):
                if folder == user_id:
                    if os.path.isdir(os.path.join("media/", folder)):
                        shutil.rmtree(os.path.join("media/", folder))

        return super().destroy(request, *args, *kwargs)


class UpdateEmployeeAPIView(UpdateAPIView, DestroyAPIView):
    model = Employee
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
    lookup_field = "employee_id"

    def put(self, request, *args, **kwargs):
        pk = self.kwargs.get("employee_id")
        if "media" in os.listdir(os.getcwd()):
            try:
                user_id = self.queryset.get(employee_id=pk).employee_id
            except ObjectDoesNotExist:
                return Response(data={"User does not exist"})
            for folder in os.listdir("media/"):
                if folder == user_id:
                    if os.path.isdir(os.path.join("media/", folder)):
                        shutil.rmtree(os.path.join("media/", folder))

        super().destroy(request, *args, *kwargs)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        idd = serializer.validated_data.get("employee_id")  # type: ignore
        path = f"media/{idd}"
        main_image_path = os.path.join(path, "main.jpg")

        images = request.FILES.get("images")
        main_image = request.FILES.get("main_image")

        if not images and not main_image:
            raise ValidationError("You must provide either 'images' or 'main_image'.")

        if images:
            if not zipfile.is_zipfile(images):
                raise ValidationError(
                    "If 'images' are provided, it must be a valid ZIP archive."
                )

            zip_file_path = os.path.join(settings.MEDIA_ROOT, f"{idd}.zip")
            with open(zip_file_path, "wb+") as destination:
                for chunk in images.chunks():
                    destination.write(chunk)

            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                image_files = [
                    file
                    for file in zip_ref.namelist()
                    if not file.endswith("/") and is_valid_image_extension(file)
                ]
                if not image_files:
                    raise ValidationError(
                        "The ZIP archive must contain valid image files."
                    )

                for file in image_files:
                    zip_ref.extract(file, path)
                    index = zip_ref.namelist().index(file)
                    new_file_path = os.path.join(path, f"{index + 1}.jpg")
                    os.rename(os.path.join(path, file), new_file_path)

            os.remove(zip_file_path)

        if main_image:
            # Создаем папку, если её нет
            os.makedirs(path, exist_ok=True)

            with open(main_image_path, "wb+") as destination:
                for chunk in main_image.chunks():
                    destination.write(chunk)

        # serializer.validated_data["main_image"] = f"{idd}/main.jpg"
        serializer.save()
        serializer.data[
            "main_image"
        ] = f"{serializer.validated_data.get('employee_id')}/main.jpg"
        return Response(serializer.data, status=status.HTTP_201_CREATED)
