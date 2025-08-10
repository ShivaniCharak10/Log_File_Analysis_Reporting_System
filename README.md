# Log Analyzer CLI & Dashboard
The Log File Analysis & Reporting System is a Python-based application with both Command-Line Interface (CLI) and Streamlit Dashboard for analyzing Apache-style web server logs.

It reads raw log files and extracts structured information such as IP addresses, timestamps, HTTP methods, URLs, status codes, and user-agent details.
The parsed data is stored in a MySQL database for efficient querying, and users can generate both tabular reports via CLI and interactive visualizations via Streamlit.

## Table of Contents
- [Introduction / Overview](#introduction--overview)
- [Objectives / Goals](#objectives--goals)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [Future Enhancements](#future-enhancements)

---

## Introduction / Overview
The Log File Analysis & Reporting System is a Python-based tool designed to parse, store, analyze, and visualize log data efficiently.  
It supports both **command-line interface (CLI)** operations and a **Streamlit-powered dashboard** for interactive data exploration.

This project can be used for monitoring application logs, tracking request patterns, identifying errors, and generating reports from log files in a structured way.

---

## Objectives / Goals
- Automate log parsing and storage in a database.
- Provide both CLI-based quick analysis and a web-based interactive dashboard.
- Offer flexible querying and filtering for large datasets.
- Enable visualization of traffic, errors, and request patterns.

---

## Features
- **CLI Tool** to parse and insert logs into MySQL database.
- **Streamlit Dashboard** for interactive analysis & visualization.
- Custom log filtering by IP, date range, status code, and method.
- Graphs showing requests per hour, top resources, and error trends.
- Ability to add new log fields (e.g., `request_time`) dynamically.
- Support for multiple log formats.
- Persistent database storage for large datasets.

---

## System Architecture
          ┌────────────────────┐
          │     Log Files      │
          │                    |
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │    Log Parser      │
          │                    │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │ Data Normalization │
          │                    │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │  MySQL Database    │
          │                    │
          │                    │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │ Streamlit Dashboard│
          │                    |
          └──────────────────  ┘
                  



---

## Technologies Used
- **Python**
- **Streamlit** – Interactive dashboard
- **MySQL** – Data storage
- **Pandas** – Data analysis
- **Plotly** – Data visualization
- **ConfigParser** – Configuration handling
- **Logging** – Event logging

---

## Prerequisites
- Python 3.8+
- MySQL server installed & running
- MySQL user credentials configured in `config.ini` or `config.json`
- Required Python packages:

pip install -r requirements.txt

---

Usage
1. Command Line Interface (CLI)

python cli.py --file access.log

2. Streamlit Dashboard

python main.py dashboard

---

## Database Schema

CREATE TABLE IF NOT EXISTS logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45),
    timestamp DATETIME,
    request_method VARCHAR(10),
    resource TEXT,
    status_code INT,
    response_size INT,
    request_time DATETIME
);

---

## Future Enhancements
- Real-time log monitoring with auto-refresh in dashboard.
- Role-based authentication for dashboard access.
- Export analytics as PDF or CSV directly from dashboard.
- Support for additional log formats like JSON & XML.
- Integration with cloud databases for scalability.

```bash
