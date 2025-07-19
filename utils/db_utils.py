"""
Module for DB related utilities
"""
from datetime import datetime

from cassandra.cluster import Cluster


from utils.cassandra_config_constants import CASSANDRA_HOSTS, CASSANDRA_PORT, KEYSPACE, TABLE_NAME
from utils.crypto_utils import decrypt, encrypt


def get_cassandra_session():
    cluster = Cluster(CASSANDRA_HOSTS, port=CASSANDRA_PORT)
    session = cluster.connect()

    # Create keyspace if it doesn't exist
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
        WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '1' }}
    """)

    session.set_keyspace(KEYSPACE)

    # Create table if it doesn't exist
    session.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            fleet_id TEXT,
            latitude TEXT,
            longitude TEXT,
            updated_at TIMESTAMP,
            speed TEXT,
            PRIMARY KEY (fleet_id, updated_at)
        ) WITH CLUSTERING ORDER BY (updated_at DESC)
    """)

    return session

def insert_location(session,fleet_id:str, latitude:float,longitude:float, speed: float):
    encrypted_lat = encrypt(str(latitude))
    encrypted_lon = encrypt(str(longitude))
    encrypted_speed = encrypt(str(speed))
    session.execute(
        f"""
        INSERT INTO {TABLE_NAME} (fleet_id, updated_at, latitude, longitude, speed)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (fleet_id, datetime.utcnow(), encrypted_lat, encrypted_lon, encrypted_speed)
    )

def get_location(session,fleet_id:str):
    query = f"""
        SELECT * FROM {TABLE_NAME}
        WHERE fleet_id = %s
        LIMIT 1
        """
    result = session.execute(query, (fleet_id,))
    row = result.one()
    if row:
        return {
            "fleet_id": row.fleet_id,
            "latitude": float(decrypt(row.latitude)),
            "longitude": float(decrypt(row.longitude)),
            "speed": float(decrypt(row.speed)),
            "updated_at": row.updated_at
        }
    return None

def fetch_recent_locations(session,fleet_id:str,limit:int=10):
    result = session.execute(
        f"""
        SELECT * FROM {TABLE_NAME}
        WHERE fleet_id = %s
        LIMIT %s
        """,
        (fleet_id, limit)
    )
    return list(result)