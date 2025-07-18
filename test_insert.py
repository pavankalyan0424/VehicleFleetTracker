from cassandra.cluster import Cluster
from datetime import datetime
import random

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('fleet_tracking')

bus_id = "PKT-123"
timestamp = datetime.utcnow()
latitude = 17.3850 + random.random() * 0.01  # Hyderabad-ish
longitude = 78.4867 + random.random() * 0.01
speed = random.uniform(30, 60)

query = """
INSERT INTO bus_tracking (bus_id, timestamp, latitude, longitude, speed)
VALUES (%s, %s, %s, %s, %s)
"""

session.execute(query, (bus_id, timestamp, latitude, longitude, speed))
print("Data inserted!")
