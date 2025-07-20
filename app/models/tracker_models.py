"""
Module for Tracker related models
"""

from datetime import datetime
from pydantic import BaseModel


class VehicleLocationUpdateRequest(BaseModel):
    latitude: float
    longitude: float
    speed: float


class VehicleLocationDetailResponse(BaseModel):
    latitude: float
    longitude: float
    updated_at: datetime
    speed: float


class VehicleLocationSnapshotResponse(VehicleLocationDetailResponse):
    vehicle_id: str


class VehicleCoordinatesResponse(BaseModel):
    latitude: float
    longitude: float
