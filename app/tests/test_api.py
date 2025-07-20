"""
Module for validating APIs
"""

import random
import requests

api_endpoint = "http://127.0.0.1:8000"
test_vehicle_id = f"VEHICLE-{random.randint(1000, 9999)}"
test_json = {
    "latitude": round(random.uniform(112.0, 113.0), 5),
    "longitude": round(random.uniform(77.0, 78.0), 5),
    "speed": round(random.uniform(30, 80), 2),
}


def test_health_check():
    response = requests.get(f"{api_endpoint}/health")
    assert response.status_code == 204


def test_dashboard():
    response = requests.get(f"{api_endpoint}/dashboard")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_update_location():
    response = requests.post(
        f"{api_endpoint}/locations/update/{test_vehicle_id}",
        json=test_json,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200, response.json()
    assert response.json()["status"] == "success"


def test_get_all_latest_locations():
    response = requests.get(f"{api_endpoint}/locations/latest/all")
    assert response.status_code == 200
    assert any(
        resp["vehicle_id"] == test_vehicle_id for resp in response.json()
    ), "Fleet not found"


def test_get_latest_location():
    response = requests.get(f"{api_endpoint}/locations/latest/{test_vehicle_id}")
    assert response.status_code == 200
    data = response.json()
    assert test_json["latitude"] == data["latitude"]
    assert test_json["longitude"] == data["longitude"]


def test_get_location_history():
    response = requests.get(f"{api_endpoint}/locations/history/{test_vehicle_id}")
    assert response.status_code == 200
    assert any(
        resp["latitude"] == test_json["latitude"]
        and resp["longitude"] == test_json["longitude"]
        for resp in response.json()
    ), "Fleet not found"


def test_get_average_speed():
    response = requests.get(f"{api_endpoint}/locations/speed/average/{test_vehicle_id}")
    assert response.status_code == 200
