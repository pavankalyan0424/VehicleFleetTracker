# Distributed, Secure Vehicle Fleet Tracker with Cassandra and FastAPI

A real-time, distributed and secure vehicle fleet tracking system leveraging Apache Cassandra and FastAPI 

> This project simulates tracking multiple vehicles, efficiently stores and retrieves their location and speed data and demonstrates concurrent data ingestion and querying in a distributed environment - with encrypted storage in Cassandra.


## 🧩 Features

* Real-time tracking of multiple vehicles
* Secure storage and retrieval of location data using AES-GCM Encryption
* Calculate average speeds and view recent movement history
* Showcase distributed database usage (Cassandra)
* Concurrent ingestion and UI updates
* Modular FastAPI backend with clean routing
* Bootstrap-powered dashboard

### Visit http://localhost:8000/dashboard for live dashboard 

## 🧱 Tech Stack
| Layer      | Technology                                        | Description                              |
|------------|---------------------------------------------------|------------------------------------------|
| Backend    | FastAPI (Python)                                  | High performance async REST API          |
| Database   | Apache Cassandra (NoSQL)                          | Distributed, Scalable, NoSQL             |
| Frontend   | HTML + Bootstrap 5 + Javascript                   | Responsive UI with Fetch API Integration |
| Data Model | vehicle_id, timestamp, latitude, longitude, speed | Data per update                          |

## 📁 Project Structure

```text
VehicleFleetTracker/
├── app/                      # Server
│   ├── models/               # Data models
│   │   └── tracker_models.py
│   ├── templates/            # Frontend UI
│   │   └── dashboard.html 
│   ├── tests/                # Tests
│   │   └── test_api.py 
│   ├── main.py               # FastAPI entrypoint
│   ├── models.py             # Data models
│   └── routes.py             # All route definitions
├── client/                   # Client Simulators
│   ├── high_load_simulator.py
│   └── low_load_simulator.py
├── utils/
│   ├── cassandra_config_constants # cassandra related constants
│   └── db_utils.py   # Cassandra connection setup
├── requirements.txt
└── README.md                 # This file!
```

## ⚙️ Setup Instructions
* Python 3.10+
* Cassandra installed (locally or remote)

## 🔧 Installation

```
git clone https://github.com/pavankalyan0424/VehicleFleetTracker.git
cd VehicleFleetTracker
pip install -r requirements.frozen.txt
```

## 🔌 Cassandra Configuration

Edit utils/cassandra_config_constants.py according to your requirements

## 🚀 Running the Server
```
uvicorn app.main:app --reload
```

## API Endpoints

> Visit http://localhost:8000/docs

| Method | Endpoint                              | Description                         |
|--------|---------------------------------------|-------------------------------------|
| GET    | /health                               | Get health of application           |
| GET    | /dashboard                            | Get dashboard                       |
| GET    | /locations/latest/all                 | Get latest location of all vehicles |
| GET    | /locations/latest/{vehicle_id}        | Get latest location for a vehicle   |
| GET    | /locations/history/{vehicle_id}       | Get last 10 locations for a vehicle |
| GET    | /locations/speed/average/{vehicle_id} | Get average speed of vehicle        |
| POST   | /locations/update/{vehicle_id}        | Update new location for a vehicle   |

## 🙌 Acknowledgements

* Apache Cassandra
* FastAPI
* Bootstrap

## 📝 Future Improvements

* Add authentication and access control
* Support real time Web-Socket Updates
* Logging and Alerting Sytem
* Map view for showing locations
* Cloud deployment and horizontal scalability