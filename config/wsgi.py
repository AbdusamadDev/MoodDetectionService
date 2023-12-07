"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import threading

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
def run_ai():
    os.system("source /home/ubuntu/Downloads/MoodDetectionService/venv/bin/activate")
    os.system(f"python /home/ubuntu/Downloads/MoodDetectionService/service/combiner.py")

p = threading.Thread(target=run_ai)
p.start()