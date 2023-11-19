from django.db.models.signals import post_save
from django.dispatch import receiver
from api.models import Employee, Camera
from api.utils import find_process_id_by_path, run_script
import psutil


@receiver(post_save, sender=Employee)
def employee_created(sender, instance, created, **kwargs):
    if created:
        path = "service/stream.py"
        pid = find_process_id_by_path(path)
        if pid:
            process = psutil.Process(pid)
            process.terminate()
        # run_script(path)
        print(f"New employee created: {instance.first_name}")


@receiver(post_save, sender=Camera)
def employee_created(sender, instance, created, **kwargs):
    if created:
        path = "service/stream.py"
        pid = find_process_id_by_path(path)
        if pid:
            process = psutil.Process(pid)
            process.terminate()
        # run_script(path)
        print(f"New employee created: {instance.name}")
