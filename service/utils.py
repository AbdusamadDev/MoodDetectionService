import socket
import cv2
import os
from datetime import datetime
from jose import jwt
from jose.exceptions import JWTError

SECRET_KEY = "your_secret_key"  # Should be kept secret and safe


def host():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        public_ip = "http://" + str(s.getsockname()[0]) + ":8000"
    except Exception:
        public_ip = "Unable to get IP"
    finally:
        s.close()
    return public_ip


def save_screenshot(frame, camera_url, path):
    if not os.path.exists(path):
        os.makedirs(path)
    timestamp = datetime.now().strftime("%Y-%m-%d|%H-%M-%S")
    filename = f"{path}/{timestamp}|{camera_url.split('/')[2]}.jpg"
    cv2.imwrite(filename, frame)
    return filename


def generate_jwt(data):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
    token = jwt.encode({'data': data, 'exp': expiration}, SECRET_KEY, algorithm='HS256')
    return token


def verify_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload  # Return the payload if token is valid
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except JWTError:
        # Token is invalid
        return None


host_address = host()
