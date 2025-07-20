"""
Module for DB related utilities
"""

from cassandra.cluster import Cluster
from datetime import datetime, UTC

from utils.cassandra_config_constants import (
    CASSANDRA_HOSTS,
    CASSANDRA_PORT,
    KEYSPACE,
    FLEET_LOCATION_TABLE,
    FLEET_LATEST_LOCATION_TABLE,
)
from utils.crypto_utils import decrypt, encrypt


def get_cassandra_session():
    cluster = Cluster(CASSANDRA_HOSTS, port=CASSANDRA_PORT)
    session = cluster.connect()

    # Create keyspace if it doesn't exist
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
            CREATE TABLE IF NOT EXISTS {FLEET_LOCATION_TABLE} (
                fleet_id TEXT,
                latitude TEXT,
                longitude TEXT,
                speed TEXT,
                updated_at TIMESTAMP,
                PRIMARY KEY (fleet_id, updated_at)
            ) WITH CLUSTERING ORDER BY (updated_at DESC)
        """
    )

    session.execute(
        f"""
            CREATE TABLE IF NOT EXISTS {FLEET_LATEST_LOCATION_TABLE} (
                fleet_id TEXT PRIMARY KEY,
                latitude TEXT,
                longitude TEXT,
                speed TEXT,
                updated_at TIMESTAMP
            )
        """
    )

    return session


def insert_location(
    session,
    fleet_id: str,
    latitude: float,
    longitude: float,
    speed: float,
):
    encrypted_lat = encrypt(str(latitude))
    encrypted_lon = encrypt(str(longitude))
    encrypted_speed = encrypt(str(speed))
    now = datetime.now(UTC)
    session.execute(
        f"""
        INSERT INTO {FLEET_LOCATION_TABLE} (fleet_id, updated_at, latitude, longitude, speed)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (fleet_id, now, encrypted_lat, encrypted_lon, encrypted_speed),
    )

    # Insert/update latest location
    session.execute(
        f"""
        INSERT INTO {FLEET_LATEST_LOCATION_TABLE} (fleet_id, updated_at, latitude, longitude, speed)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (fleet_id, now, encrypted_lat, encrypted_lon, encrypted_speed),
    )


def get_all_latest_locations(session):
    query = f"""
            SELECT * FROM {FLEET_LATEST_LOCATION_TABLE}
            """
    rows = session.execute(query)
    result = []

    for row in rows:
        result.append(
            {
                "fleet_id": row.fleet_id,
                "latitude": float(decrypt(row.latitude)),
                "longitude": float(decrypt(row.longitude)),
                "speed": float(decrypt(row.speed)),
                "updated_at": row.updated_at.isoformat(),
            }
        )
    result.sort(key=lambda x: x["fleet_id"])
    return result


def get_latest_location(session, fleet_id: str):
    query = f"""
        SELECT * FROM {FLEET_LATEST_LOCATION_TABLE}
        WHERE fleet_id = %s
        """
    result = session.execute(query, (fleet_id,))
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
    session,
    fleet_id: str,
    limit: int = 10,
):
    rows = session.execute(
        f"""
        SELECT * FROM {FLEET_LOCATION_TABLE}
        WHERE fleet_id = %s
        LIMIT %s
        """,
        (fleet_id, limit),
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


def fetch_recent_speeds(session, fleet_id: str, limit: int = 10):
    rows = session.execute(
        f"""
                SELECT speed FROM {FLEET_LOCATION_TABLE}
                WHERE fleet_id = %s LIMIT %s
            """,
        (fleet_id, limit),
    )

    return [float(decrypt(row.speed)) for row in rows if row.speed]
