"""
Module for generating low load
"""

import time
import random
import requests
from concurrent.futures import ThreadPoolExecutor

API_URL = "http://127.0.0.1:8000/locations/update"


# Simulate a single vehicle
def simulate_vehicle(vehicle_id):
    for _ in range(10):
        latitude = round(random.uniform(112.0, 113.0), 5)
        longitude = round(random.uniform(77.0, 78.0), 5)
        speed = round(random.uniform(30, 80), 2)
        data = {
            "latitude": latitude,
            "longitude": longitude,
            "speed": speed,
        }
        try:
            res = requests.post(f"{API_URL}/{vehicle_id}", json=data)
            print(f"[{vehicle_id}] Status: {res.status_code} | Response: {res.text}")
        except Exception as e:
            print(f"[{vehicle_id}] Error: {e}")
        time.sleep(2)


# Launch multiple vehicles concurrently
def run_simulation(vehicle_count=10):
    with ThreadPoolExecutor(max_workers=vehicle_count) as executor:
        vehicle_ids = [f"FLEET-{i:03}" for i in range(1, vehicle_count + 1)]
        executor.map(simulate_vehicle, vehicle_ids)


if __name__ == "__main__":
    run_simulation()
