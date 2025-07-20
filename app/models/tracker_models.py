"""
Module for Tracker related models
"""

from datetime import datetime
from pydantic import BaseModel


class FleetLocationUpdateRequest(BaseModel):
    latitude: float
    longitude: float
    speed: float


class FleetLocationDetailResponse(BaseModel):
    latitude: float
    longitude: float
    updated_at: datetime
    speed: float


class FleetLocationSnapshotResponse(FleetLocationDetailResponse):
    fleet_id: str


class FleetCoordinatesResponse(BaseModel):
    latitude: float
    longitude: float
