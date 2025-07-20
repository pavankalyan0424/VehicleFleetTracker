"""
Module for tracker related APIs
"""

from typing import List
from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.templating import Jinja2Templates

from app.models.tracker_models import (
    FleetLocationUpdateRequest,
    FleetLocationDetailResponse,
    FleetLocationSnapshotResponse,
    FleetCoordinatesResponse,
)
from utils.db_utils import (
    get_cassandra_session,
    get_latest_location,
    insert_location,
    fetch_recent_speeds,
    get_all_latest_locations,
    fetch_recent_locations,
)

router = APIRouter()
session = get_cassandra_session()
templates = Jinja2Templates(directory="templates")


@router.get("/health")
def health() -> Response:
    return Response(status_code=204)


@router.get("/dashboard")
def dashboard_view(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.post("/locations/update/{fleet_id}", response_model=None)
def update_fleet_location_by_fleet_id(
    fleet_id: str,
    data: FleetLocationUpdateRequest,
):
    try:
        insert_location(session, fleet_id, data.latitude, data.longitude, data.speed)
        return {"status": "success", "message": "Location updated"}
    except Exception as exception:
        raise HTTPException(
            status_code=500, detail=f"Updating location failed with Error {exception}"
        )


@router.get("/locations/latest/all", response_model=List[FleetLocationSnapshotResponse])
def get_all_fleet_locations():
    try:
        return get_all_latest_locations(session)
    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=f"Fetching latest locations failed with Error {exception}",
        )


@router.get("/locations/latest/{fleet_id}", response_model=FleetLocationDetailResponse)
def get_fleet_latest_location_by_fleet_id(
    fleet_id: str,
):
    try:
        location = get_latest_location(session, fleet_id)
        if location:
            return location
        raise HTTPException(
            status_code=404, detail=f"Fleet with ID {fleet_id} not found"
        )
    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=f"Fetching latest location failed with Error {exception}",
        )


@router.get(
    "/locations/history/{fleet_id}", response_model=List[FleetCoordinatesResponse]
)
def get_fleet_history_by_fleet_id(
    fleet_id: str,
):
    try:
        location = fetch_recent_locations(session, fleet_id)
        if location:
            return location
        raise HTTPException(
            status_code=404, detail=f"Fleet with ID {fleet_id} not found"
        )
    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=f"Fetching latest location failed with Error {exception}",
        )


@router.get("/locations/speed/average/{fleet_id}")
def get_average_speed_by_fleet_id(
    fleet_id: str,
):
    try:
        speeds = fetch_recent_speeds(session, fleet_id)
        if not speeds:
            raise HTTPException(status_code=404, detail="No data found")

        avg_speed = sum(speeds) / len(speeds)

        return {"avg_speed": round(avg_speed, 2), "samples": len(speeds)}
    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=f"Fetching average speed failed with Error {exception}",
        )
