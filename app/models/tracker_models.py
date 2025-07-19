"""
Module for Tracker related models
"""
from pydantic import BaseModel, Field
from datetime import datetime

class FleetLocationUpdate(BaseModel):
    fleet_id: str
    latitude: float
    longitude: float
    speed: int

class FleetLocationResponse(BaseModel):
    latitude: float
    longitude: float
    updated_at: datetime