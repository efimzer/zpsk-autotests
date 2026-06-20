import requests

payload = {
  "phone": "+79502526000",
  "code": "2526"
}

response = requests.post(
    "https://stage.zapaska.online/auth/login",
    json = payload
    )

print(response.status_code)
print(response.headers["Set-Cookie"])
print(response.json())