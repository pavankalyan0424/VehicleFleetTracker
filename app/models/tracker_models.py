"""
Module for Tracker related models
"""
from pydantic import BaseModel, Field
from datetime import datetime

class FleetLocationUpdate(BaseModel):
    latitude: float
    longitude: float
    speed: float

class FleetLocationResponse(BaseModel):
    latitude: float
    longitude: float
    updated_at: datetime
    speed: float