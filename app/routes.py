"""
Module for tracker related APIs
"""

from typing import List
from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.templating import Jinja2Templates

from app.models.tracker_models import (
    VehicleLocationUpdateRequest,
    VehicleLocationDetailResponse,
    VehicleLocationSnapshotResponse,
    VehicleCoordinatesResponse,
)
from utils.db_utils import DBUtils

db_utils = DBUtils()
db_utils.init_session()
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/health")
def health() -> Response:
    return Response(status_code=204)


@router.get("/dashboard")
def dashboard_view(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.post("/locations/update/{vehicle_id}", response_model=None)
def update_vehicle_location_by_vehicle_id(
    vehicle_id: str,
    data: VehicleLocationUpdateRequest,
):
    try:
        db_utils.insert_location(vehicle_id, data.latitude, data.longitude, data.speed)
        return {"status": "success", "message": "Location updated"}
    except Exception as exception:
        raise HTTPException(
            status_code=500, detail=f"Updating location failed with Error {exception}"
        )


@router.get("/locations/latest/all", response_model=List[VehicleLocationSnapshotResponse])
def get_all_vehicle_locations():
    try:
        return db_utils.get_all_latest_locations()
    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=f"Fetching latest locations failed with Error {exception}",
        )


@router.get(
    "/locations/latest/{vehicle_id}", response_model=VehicleLocationDetailResponse
)
def get_vehicle_latest_location_by_vehicle_id(
    vehicle_id: str,
):
    try:
        location = db_utils.get_latest_location(vehicle_id)
        if location:
            return location
        raise HTTPException(
            status_code=404, detail=f"Vehicle with ID {vehicle_id} not found"
        )
    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=f"Fetching latest location failed with Error {exception}",
        )


@router.get(
    "/locations/history/{vehicle_id}", response_model=List[VehicleCoordinatesResponse]
)
def get_vehicle_history_by_vehicle_id(
    vehicle_id: str,
):
    try:
        location = db_utils.fetch_recent_locations(vehicle_id)
        if location:
            return location
        raise HTTPException(
            status_code=404, detail=f"Vehicle with ID {vehicle_id} not found"
        )
    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=f"Fetching latest location failed with Error {exception}",
        )


@router.get("/locations/speed/average/{vehicle_id}")
def get_average_speed_by_vehicle_id(
    vehicle_id: str,
):
    try:
        speeds = db_utils.fetch_recent_speeds(vehicle_id)
        if not speeds:
            raise HTTPException(status_code=404, detail="No data found")

        avg_speed = sum(speeds) / len(speeds)

        return {"avg_speed": round(avg_speed, 2), "samples": len(speeds)}
    except Exception as exception:
        raise HTTPException(
            status_code=500,
            detail=f"Fetching average speed failed with Error {exception}",
        )
