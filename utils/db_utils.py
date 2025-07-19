"""
Module for DB related utilities
"""
from cassandra.cluster import Cluster
from datetime import datetime



from utils.cassandra_config_constants import (
    CASSANDRA_HOSTS,
    CASSANDRA_PORT,
    KEYSPACE,
    TABLE_NAME,
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
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
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
        """
    CREATE TABLE IF NOT EXISTS fleet_location_latest (
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
    session, fleet_id: str, latitude: float, longitude: float, speed: float
):
    encrypted_lat = encrypt(str(latitude))
    encrypted_lon = encrypt(str(longitude))
    encrypted_speed = encrypt(str(speed))
    now = datetime.utcnow()
    session.execute(
        f"""
        INSERT INTO {TABLE_NAME} (fleet_id, updated_at, latitude, longitude, speed)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (fleet_id, now, encrypted_lat, encrypted_lon, encrypted_speed),
    )

    # Insert/update latest location
    session.execute(
        """
        INSERT INTO fleet_location_latest (fleet_id, updated_at, latitude, longitude, speed)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (fleet_id, now, encrypted_lat, encrypted_lon, encrypted_speed),
    )


def get_all_latest_locations(session):
    query = """
            SELECT * FROM fleet_location_latest
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
        SELECT * FROM fleet_location_latest
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


def fetch_recent_locations(session, fleet_id: str, limit: int = 10):
    rows = session.execute(
        f"""
        SELECT * FROM {TABLE_NAME}
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
                SELECT speed FROM fleet_location 
                WHERE fleet_id = %s LIMIT %s
            """,
        (fleet_id, limit),
    )

    return [float(decrypt(row.speed)) for row in rows if row.speed]
