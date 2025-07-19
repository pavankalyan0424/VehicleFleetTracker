"""
Module for tracker related APIs
"""

from fastapi import APIRouter, HTTPException, Response

from app.models.tracker_models import FleetLocationUpdate, FleetLocationResponse
from utils.db_utils import get_cassandra_session,get_location,insert_location
router = APIRouter()
session = get_cassandra_session()

@router.get("/health")
def health() -> Response:
    return Response(status_code=204)

@router.post("/update",response_model=None)
def update_fleet_location(data: FleetLocationUpdate):
    try:
        insert_location(session,data.fleet_id,data.latitude,data.longitude,data.speed)
        return {"status":"success", "message":"Location updated"}
    except Exception as exception:
        raise HTTPException(status_code=500,detail=f"Updating location failed with Error {exception}")

@router.get("/location/{fleet_id}",response_model=FleetLocationResponse)
def get_fleet_location_by_fleet_id(fleet_id: str):
    try:
        location = get_location(session,fleet_id)
        if location:
            return location
        raise HTTPException(status_code=404,detail=f"Fleet with ID {fleet_id} not found")
    except Exception as exception:
        raise HTTPException(status_code=500, detail=f"Fetching location failed with Error {exception}")