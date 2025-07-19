import requests
import random
import time
import threading
from datetime import datetime

API_URL = "http://127.0.0.1:8000/update"

# Simulate fleets
BUS_IDS = [f"FLEET-{str(i).zfill(3)}" for i in range(1, 50)]

def generate_random_location():
    # You can center this around a city (e.g., Hyderabad)
    base_lat, base_lon = 17.385044, 78.486671
    return (
        base_lat + random.uniform(-0.05, 0.05),
        base_lon + random.uniform(-0.05, 0.05)
    )

def simulate_fleet(fleet_id):
    while True:
        latitude, longitude = generate_random_location()
        speed = round(random.uniform(20, 80), 2)
        updated_at = datetime.utcnow().isoformat()

        data = {
            "fleet_id": fleet_id,
            "latitude": latitude,
            "longitude": longitude,
            "speed": speed,
            "updated_at": updated_at
        }

        try:
            response = requests.post(f"{API_URL}/{fleet_id}", json=data)
            print(f"[{fleet_id}] {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[{fleet_id}] Error: {e}")

        time.sleep(random.uniform(1.5, 3.5))  # simulate real delay between updates

def run_simulation():
    threads = []
    for fleet_id in BUS_IDS:
        t = threading.Thread(target=simulate_fleet, args=(fleet_id,))
        t.daemon = True
        t.start()
        threads.append(t)

    # Let it run for 30 seconds
    time.sleep(30)


if __name__ == "__main__":
    run_simulation()
