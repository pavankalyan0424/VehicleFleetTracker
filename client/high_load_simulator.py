"""
Module for simulating high load
"""

import random
import threading
import time
import requests

API_URL = "http://127.0.0.1:8000/locations/update"

# Simulate fleets
FLEET_IDS = [f"FLEET-{str(i).zfill(3)}" for i in range(1, 501)]


def generate_random_location():
    # Currently points are centered around Bangalore
    base_lat, base_lon = 112.9716, 77.5946
    return (
        base_lat + random.uniform(-0.05, 0.05),
        base_lon + random.uniform(-0.05, 0.05),
    )


def simulate_fleet(fleet_id):
    while True:
        latitude, longitude = generate_random_location()
        speed = round(random.uniform(20, 80), 2)

        data = {
            "latitude": latitude,
            "longitude": longitude,
            "speed": speed,
        }

        try:
            response = requests.post(f"{API_URL}/{fleet_id}", json=data)
            print(f"[{fleet_id}] {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[{fleet_id}] Error: {e}")

        time.sleep(random.uniform(5.5, 10.5))  # simulate real delay between updates


def run_simulation():
    threads = []
    for fleet_id in FLEET_IDS:
        t = threading.Thread(target=simulate_fleet, args=(fleet_id,))
        t.daemon = True
        t.start()
        threads.append(t)

    time.sleep(300)


if __name__ == "__main__":
    run_simulation()
