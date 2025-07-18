from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from datetime import datetime, timedelta
import random
import time

KEYSPACE = "fleet_tracking"
TABLE = "bus_tracking"

def setup_cassandra():
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()

    # Drop keyspace if exists
    session.execute(f"DROP KEYSPACE IF EXISTS {KEYSPACE}")

    # Create keyspace
    session.execute(f"""
    CREATE KEYSPACE {KEYSPACE}
    WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': 1 }}
    """)

    session.set_keyspace(KEYSPACE)

    # Create table
    session.execute(f"""
    CREATE TABLE {TABLE} (
        bus_id TEXT,
        timestamp TIMESTAMP,
        latitude DOUBLE,
        longitude DOUBLE,
        speed DOUBLE,
        PRIMARY KEY (bus_id, timestamp)
    ) WITH CLUSTERING ORDER BY (timestamp DESC)
    """)

    return session

def simulate_gps_data(session, bus_id, count=10, delay=0.5):
    insert_query = session.prepare(f"""
        INSERT INTO {TABLE} (bus_id, timestamp, latitude, longitude, speed)
        VALUES (?, ?, ?, ?, ?)
    """)
    base_lat, base_long = 17.3850, 78.4867

    for i in range(count):
        timestamp = datetime.utcnow()
        lat = base_lat + random.uniform(-0.01, 0.01)
        long = base_long + random.uniform(-0.01, 0.01)
        speed = random.uniform(30, 80)

        session.execute(insert_query, (bus_id, timestamp, lat, long, speed))
        print(f"[{bus_id}] Inserted point #{i+1} at {timestamp}")
        time.sleep(delay)

def get_latest_location(session, bus_id):
    query = f"""
    SELECT * FROM {TABLE}
    WHERE bus_id = %s
    LIMIT 1
    """
    result = session.execute(query, (bus_id,))
    for row in result:
        print(f"Latest location of {bus_id}: {row.latitude}, {row.longitude} at {row.timestamp} (Speed: {row.speed:.2f} km/h)")

if __name__ == "__main__":
    session = setup_cassandra()

    # Simulate 3 buses
    bus_ids = ["PKT-101", "PKT-202", "PKT-303"]
    for bus_id in bus_ids:
        simulate_gps_data(session, bus_id, count=20)

    # Query latest location
    print("\n🔍 Querying latest locations:")
    for bus_id in bus_ids:
        get_latest_location(session, bus_id)