# EV Battery Health Monitoring and Recommendation System

A database-driven system to monitor and manage Electric Vehicle battery health using Advanced Database Management techniques in PostgreSQL, with automated alerts, role-based access control, and a Streamlit dashboard.

## Overview

This project demonstrates how ADBMS concepts including indexing, triggers, partitioning, and row-level security can be applied to build a scalable and secure EV battery monitoring system. It includes rule-based car recommendations and a basic ML model for battery degradation prediction.

## Features

### Indexing
- B-Tree index on `vehicle_id` for faster query performance
- Verified using `EXPLAIN ANALYZE`

### Triggers (ECA Model)
- Automatically inserts an alert into `battery_alerts` when SOH drops below 80%

### Security (RBAC + RLS)
- **Admin:** full access
- **Technician:** insert and update
- **Driver:** view own data only
- Row-Level Security ensures users access only permitted records

### Partitioning
- Table partitioned by date (monthly)
- Improves scalability using partition pruning

### Battery Performance Analysis
- Time-series data stored using timestamps
- Health vs time, temperature trends, usage patterns

### Car Recommendation System
| SOH | Recommendation |
|---|---|
| Above 80% | Continue using vehicle |
| 60-80% | Suggest similar EV |
| Below 60% | Recommend upgrade |

### Machine Learning
- Predicts future battery health using SOH, temperature, and charge cycles

## Database Schema

**Tables:** `battery_readings`, `battery_alerts`, `cars`

**Key fields:** `vehicle_id`, `soh`, `temperature`, `voltage`, `timestamp`

## Alert System Flow

```
INSERT battery_reading
        |
Trigger checks SOH
        |
   SOH < 80%?
        |
Insert into battery_alerts
        |
Dashboard displays alert
```

## Tech Stack

| Layer | Technology |
|---|---|
| Database | PostgreSQL |
| Backend | Python |
| Dashboard | Streamlit |
| Tools | pgAdmin |

## Project Structure

```
EV_BATTERY_PROJECT2/
├── backend/          # Python backend and ML degradation model
├── dashboard/        # Streamlit dashboard
├── sql/              # Schema, triggers, partitioning, RBAC/RLS scripts
├── requirements.txt
└── README.md
```

## Future Scope
- Cloud deployment on AWS or GCP
- Real-time IoT sensor integration
- Mobile app notifications
- Advanced ML models for degradation forecasting

## Author

**Palak Adsul**
B.Tech Computer Engineering (AI/ML Specialization), Vidyalankar Institute of Technology
