from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from typing import List

app = FastAPI()

def get_db_connection():
    try:
        connection = psycopg2.connect(
            dbname="netban",
            user="postgres",
            password="33803770",
            host="localhost",
            port="5432"
        )
        return connection
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

class VulnerabilityInput(BaseModel):
    title: str
    endpoint: str
    severity: str
    cve: str
    description: str
    sensor: str

class VulnerabilityOutput(BaseModel):
    title: str
    endpoint: str
    tag: str
    severity: str
    cve: str
    description: str
    sensor: str

@app.get("/vulnerabilities/", response_model=List[VulnerabilityOutput])
async def get_vulnerabilities():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        query = """
        SELECT
            title,
            endpoint,
            severity,
            cve,
            description,
            sensor
        FROM vulnerabilities
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        grouped_data = {}
        result = []
        for row in rows:
            key = row["endpoint"]
            if key not in grouped_data:
                grouped_data[key] = f"group_{len(grouped_data) + 1}"

            result.append({
                "title": row["title"],
                "endpoint": row["endpoint"],
                "tag": grouped_data[key],
                "severity": row["severity"],
                "cve": row["cve"],
                "description": row["description"],
                "sensor": row["sensor"]
            })

        cursor.close()
        connection.close()
        return result

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.post("/vulnerabilities/")
async def add_vulnerability(vulnerability: VulnerabilityInput):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        insert_query = """
        INSERT INTO vulnerabilities (title, endpoint, severity, cve, description, sensor)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (
            vulnerability.title,
            vulnerability.endpoint,
            vulnerability.severity,
            vulnerability.cve,
            vulnerability.description,
            vulnerability.sensor
        ))
        connection.commit()

        cursor.close()
        connection.close()
        return {"message": "Vulnerability added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add vulnerability: {e}")

@app.delete("/vulnerabilities/{vulnerability_id}")
async def delete_vulnerability(vulnerability_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        delete_query = """
        DELETE FROM vulnerabilities
        WHERE id = %s;
        """
        cursor.execute(delete_query, (vulnerability_id,))
        connection.commit()

        cursor.close()
        connection.close()
        return {"message": "Vulnerability deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete vulnerability: {e}")

@app.put("/vulnerabilities/{vulnerability_id}")
async def update_vulnerability(vulnerability_id: int, vulnerability: VulnerabilityInput):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        update_query = """
        UPDATE vulnerabilities
        SET title = %s, endpoint = %s, severity = %s, cve = %s, description = %s, sensor = %s
        WHERE id = %s;
        """
        cursor.execute(update_query, (
            vulnerability.title,
            vulnerability.endpoint,
            vulnerability.severity,
            vulnerability.cve,
            vulnerability.description,
            vulnerability.sensor,
            vulnerability_id
        ))
        connection.commit()

        cursor.close()
        connection.close()
        return {"message": "Vulnerability updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update vulnerability: {e}")
