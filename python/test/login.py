import requests

token_url = "http://10.100.1.30:8080/realms/MIHIRA-REALM/protocol/openid-connect/token"

payload = {
    "grant_type": "password",
    "client_id": "mihira-cli",
    "username": "bob",
    "password": "1234",
}

resp = requests.post(token_url, data=payload)
print("Status:", resp.status_code)
print("Text:", resp.text)
