from flask import Flask, request, jsonify
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from datetime import datetime

app = Flask(__name__)

# Cassandra setup
KEYSPACE = "fleet_tracking"
TABLE = "bus_tracking"
cluster = Cluster(['127.0.0.1'])
session = cluster.connect(KEYSPACE)

# Insert endpoint
@app.route("/update_location", methods=["POST"])
def update_location():
    data = request.get_json()
    bus_id = data.get("bus_id")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    speed = data.get("speed")
    timestamp = datetime.utcnow()

    if not all([bus_id, latitude, longitude, speed]):
        return jsonify({"error": "Missing fields"}), 400

    query = session.prepare(f"""
        INSERT INTO {TABLE} (bus_id, timestamp, latitude, longitude, speed)
        VALUES (?, ?, ?, ?, ?)
    """)
    session.execute(query, (bus_id, timestamp, latitude, longitude, speed))
    return jsonify({"status": "success", "timestamp": timestamp.isoformat()}), 200

# Query endpoint
@app.route("/location/<bus_id>", methods=["GET"])
def get_latest_location(bus_id):
    query = f"""
    SELECT * FROM {TABLE}
    WHERE bus_id = %s
    LIMIT 1
    """
    result = session.execute(query, (bus_id,))
    row = result.one()

    if row:
        return jsonify({
            "bus_id": row.bus_id,
            "timestamp": row.timestamp.isoformat(),
            "latitude": row.latitude,
            "longitude": row.longitude,
            "speed": row.speed
        })
    else:
        return jsonify({"error": "No data found"}), 404

if __name__ == "__main__":
    app.run(debug=True)