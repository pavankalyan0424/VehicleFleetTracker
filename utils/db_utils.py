"""
Module for DB related utilities
"""

from cassandra.cluster import Cluster
from datetime import datetime, UTC

from utils.cassandra_config_constants import (
    CASSANDRA_HOSTS,
    CASSANDRA_PORT,
    KEYSPACE,
    VEHICLE_LOCATION_TABLE,
    VEHICLE_LATEST_LOCATION_TABLE,
)
from utils.crypto_utils import decrypt, encrypt


class DBUtils:

    def __init__(self):
        self.session = None

    def init_session(self):
        cluster = Cluster(CASSANDRA_HOSTS, port=CASSANDRA_PORT)
        session = cluster.connect()
        session.execute(
            f"""
                    CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
                    WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '1' }}
                """
        )

        session.set_keyspace(KEYSPACE)

        # Create tables if it doesn't exist
        session.execute(
            f"""
                    CREATE TABLE IF NOT EXISTS {VEHICLE_LOCATION_TABLE} (
                        vehicle_id TEXT,
                        latitude TEXT,
                        longitude TEXT,
                        speed TEXT,
                        updated_at TIMESTAMP,
                        PRIMARY KEY (vehicle_id, updated_at)
                    ) WITH CLUSTERING ORDER BY (updated_at DESC)
                """
        )

        session.execute(
            f"""
                    CREATE TABLE IF NOT EXISTS {VEHICLE_LATEST_LOCATION_TABLE} (
                        vehicle_id TEXT PRIMARY KEY,
                        latitude TEXT,
                        longitude TEXT,
                        speed TEXT,
                        updated_at TIMESTAMP
                    )
                """
        )
        self.session = session

    def insert_location(
        self,
        vehicle_id: str,
        latitude: float,
        longitude: float,
        speed: float,
    ):
        encrypted_lat = encrypt(str(latitude))
        encrypted_lon = encrypt(str(longitude))
        encrypted_speed = encrypt(str(speed))
        now = datetime.now(UTC)
        self.session.execute(
            f"""
            INSERT INTO {VEHICLE_LOCATION_TABLE} (vehicle_id, updated_at, latitude, longitude, speed)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (vehicle_id, now, encrypted_lat, encrypted_lon, encrypted_speed),
        )

        # Insert/update latest location
        self.session.execute(
            f"""
            INSERT INTO {VEHICLE_LATEST_LOCATION_TABLE} (vehicle_id, updated_at, latitude, longitude, speed)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (vehicle_id, now, encrypted_lat, encrypted_lon, encrypted_speed),
        )

    def get_all_latest_locations(self):
        query = f"""
                SELECT * FROM {VEHICLE_LATEST_LOCATION_TABLE}
                """
        rows = self.session.execute(query)
        result = []

        for row in rows:
            result.append(
                {
                    "vehicle_id": row.vehicle_id,
                    "latitude": float(decrypt(row.latitude)),
                    "longitude": float(decrypt(row.longitude)),
                    "speed": float(decrypt(row.speed)),
                    "updated_at": row.updated_at.isoformat(),
                }
            )
        result.sort(key=lambda x: x["vehicle_id"])
        return result

    def get_latest_location(self, vehicle_id: str):
        query = f"""
            SELECT * FROM {VEHICLE_LATEST_LOCATION_TABLE}
            WHERE vehicle_id = %s
            """
        result = self.session.execute(query, (vehicle_id,))
        row = result.one()
        if row:
            return {
                "latitude": float(decrypt(row.latitude)),
                "longitude": float(decrypt(row.longitude)),
                "speed": float(decrypt(row.speed)),
                "updated_at": row.updated_at,
            }
        return None

    def fetch_recent_locations(
        self,
        vehicle_id: str,
        limit: int = 10,
    ):
        rows = self.session.execute(
            f"""
            SELECT * FROM {VEHICLE_LOCATION_TABLE}
            WHERE vehicle_id = %s
            LIMIT %s
            """,
            (vehicle_id, limit),
        )
        result = []
        for row in rows:
            result.append(
                {
                    "latitude": float(decrypt(row.latitude)),
                    "longitude": float(decrypt(row.longitude)),
                }
            )
        return result

    def fetch_recent_speeds(self, vehicle_id: str, limit: int = 10):
        rows = self.session.execute(
            f"""
                    SELECT speed FROM {VEHICLE_LOCATION_TABLE}
                    WHERE vehicle_id = %s LIMIT %s
                """,
            (vehicle_id, limit),
        )
        return [float(decrypt(row.speed)) for row in rows if row.speed]
