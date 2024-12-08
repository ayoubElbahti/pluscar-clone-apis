
import requests
import time

url = "https://eliterent-car.onrender.com/"
i = 0
for _ in range(1):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"{url} is down! Status code: {response.status_code}  {i}")
        i = i + 1
    except requests.exceptions.RequestException as e:
        print(f"{url} is down! Error: {e}")
    time.sleep(60 / 100)  # Wait for 0.6 seconds to achieve 100 requests per minute
