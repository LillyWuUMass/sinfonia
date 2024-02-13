from yarl import URL

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
lh = URL("http://" + s.getsockname()[0])
print("localhost", lh)
s.close()

import os
import requests

url = URL("http://10.43.56.130") / "api/v1/deploy/00000000-0000-0000-0000-000000000000/B2TTXJ1TiOMXryUUFB2BZ0RKRzQC_0T2jkOuWPWGizw"

response = requests.post(url)

if response.status_code == 200:
    print("POST request successful!")
else:
    print("POST request failed with status code:", response.status_code)
    