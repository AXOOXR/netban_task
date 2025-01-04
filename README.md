# Vulnerabilities API

This FastAPI application provides a RESTful API for managing and retrieving information about vulnerabilities. The API supports operations such as creating, reading, updating, and deleting vulnerability records stored in a PostgreSQL database.

The vulnerability grouping process is done using `TF-IDF` for feature extraction, `SVD` for dimensionality reduction, and `DBSCAN` for clustering similar vulnerabilities together. Vulnerabilities are grouped by endpoint and then by text similarity.

## Features

- **Add Vulnerability**: Create new vulnerability records with details like title, endpoint, severity, and more.
- **Retrieve Vulnerabilities**: Fetch a list of vulnerabilities grouped and tagged by their endpoint.
- **Update Vulnerability**: Update an existing vulnerability record.
- **Delete Vulnerability**: Remove a vulnerability record by its unique ID.


## Setup

Follow the steps below to run the project locally:

## Prerequisites

- Python 3.8+
- PostgreSQL
- `pip` (Python package installer)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repository/vulnerabilities-api.git
   cd vulnerabilities-api
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your PostgreSQL database and update the connection parameters in the `get_db_connection` function.

## Database Setup

Create the `vulnerabilities` table in your PostgreSQL database:

```sql
CREATE TABLE vulnerabilities (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    severity TEXT NOT NULL,
    cve TEXT NOT NULL,
    description TEXT,
    sensor TEXT
);
```

## Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000/`.

## Endpoints

### 1. Add Vulnerability
**POST** `/vulnerabilities/`

**Request Body:**
```json
{
  "title": "XSS in profile picture",
  "endpoint": "/profile",
  "severity": "High",
  "cve": "CVE-2023-XXXX",
  "description": "Cross-site scripting vulnerability in profile picture upload.",
  "sensor": "Sensor A"
}
```

**Response:**
```json
{
  "message": "Vulnerability added successfully"
}
```

### 2. Retrieve Vulnerabilities
**GET** `/vulnerabilities/`

**Response:**
```json
[
  {
    "title": "XSS in profile picture",
    "endpoint": "/profile",
    "tag": "group_1",
    "severity": "High",
    "cve": "CVE-2023-XXXX",
    "description": "Cross-site scripting vulnerability in profile picture upload.",
    "sensor": "Sensor A"
  }
]
```

### 3. Update Vulnerability
**PUT** `/vulnerabilities/{vulnerability_id}`

**Request Body:**
```json
{
  "title": "Updated XSS in profile picture",
  "endpoint": "/profile",
  "severity": "Critical",
  "cve": "CVE-2023-YYYY",
  "description": "Updated description.",
  "sensor": "Sensor B"
}
```

**Response:**
```json
{
  "message": "Vulnerability updated successfully"
}
```

### 4. Delete Vulnerability
**DELETE** `/vulnerabilities/{vulnerability_id}`

**Response:**
```json
{
  "message": "Vulnerability deleted successfully"
}
```

## Testing

You can test the API using tools like [Postman](https://www.postman.com/) or [curl](https://curl.se/). Additionally, FastAPI provides interactive API documentation:


- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`








---




