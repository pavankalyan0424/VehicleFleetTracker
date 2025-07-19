"""
Module for tracker related APIs
"""

from fastapi import APIRouter, HTTPException, Response

from app.models.tracker_models import FleetLocationUpdate, FleetLocationResponse
from utils.db_utils import get_cassandra_session, get_latest_location, insert_location, fetch_recent_speeds, \
    get_all_latest_locations

router = APIRouter()
session = get_cassandra_session()


@router.get("/health")
def health() -> Response:
    return Response(status_code=204)


@router.post("/update/{fleet_id}", response_model=None)
def update_fleet_location_by_fleet_id(fleet_id, data: FleetLocationUpdate):
    try:
        insert_location(session, fleet_id, data.latitude, data.longitude, data.speed)
        return {"status": "success", "message": "Location updated"}
    except Exception as exception:
        raise HTTPException(status_code=500, detail=f"Updating location failed with Error {exception}")


@router.get("/location/latest/all")
def get_all_fleet_locations():
    try:
        return get_all_latest_locations(session)
    except Exception as exception:
        raise HTTPException(status_code=500, detail=f"Fetching latest locations failed with Error {exception}")


@router.get("/location/latest/{fleet_id}", response_model=FleetLocationResponse)
def get_fleet_latest_location_by_fleet_id(fleet_id: str):
    try:
        location = get_latest_location(session, fleet_id)
        if location:
            return location
        raise HTTPException(status_code=404, detail=f"Fleet with ID {fleet_id} not found")
    except Exception as exception:
        raise HTTPException(status_code=500, detail=f"Fetching latest location failed with Error {exception}")


@router.get("/location/speed/average/{fleet_id}")
def get_average_speed_by_fleet_id(fleet_id: str):
    try:
        speeds = fetch_recent_speeds(session, fleet_id)
        if not speeds:
            raise HTTPException(status_code=404, detail="No data found")

        avg_speed = sum(speeds) / len(speeds)

        return {
            "avg_speed": round(avg_speed, 2),
            "samples": len(speeds)
        }
    except Exception as exception:
        raise HTTPException(status_code=500, detail=f"Fetching average speed failed with Error {exception}")
