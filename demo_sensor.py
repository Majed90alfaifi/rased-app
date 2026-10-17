import requests
import time

SEND_READING_INTERVAL = 60  # كل دقيقة يرسل قراءة

readings = [
    {
        "pond_id": 1,
        "temperature": 28,
        "ph": 7.5,
        "ammonia": 1.0,
        "water_level": 90,
        "dissolved_oxygen": 7.0
    },
    {
        "pond_id": 1,
        "temperature": 28,
        "ph": 7.3,
        "ammonia": 1.8,
        "water_level": 88,
        "dissolved_oxygen": 6.4
    },
    {
        "pond_id": 1,
        "temperature": 28,
        "ph": 7.0,
        "ammonia": 3.5,
        "water_level": 82,
        "dissolved_oxygen": 5.6
    },
    {
        "pond_id": 1,
        "temperature": 28,
        "ph": 6.7,
        "ammonia": 5.8,
        "water_level": 70,
        "dissolved_oxygen": 4.4
    },
    {
        "pond_id": 1,
        "temperature": 35.1,
        "ph": 6.1,
        "ammonia": 8.4,
        "water_level": 55,
        "dissolved_oxygen": 3.1
    }
]

while True:
    for reading in readings:
        response = requests.post(
            "http://127.0.0.1:5000/reading",
            json=reading
        )

        print("Sent:", reading)
        print(response.status_code, response.text)

        time.sleep(SEND_READING_INTERVAL)