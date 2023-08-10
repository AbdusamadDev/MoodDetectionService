import requests

request = requests.post(
    "http://192.168.1.83:12345/api/login/",
    json={"username": "user", "password": "0000"},
)

print(request.json())
