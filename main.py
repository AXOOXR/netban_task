from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import DBSCAN
from collections import defaultdict
import os
from typing import List

app = FastAPI()

# Database connection
def get_db_connection():
    try:
        connection = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "netban"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "33803770"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        return connection
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

# Models
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

# Vulnerability grouping endpoint
@app.get("/vulnerabilities/", response_model=List[VulnerabilityOutput])
async def get_vulnerabilities():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        # Fetch vulnerabilities
        query = """
        SELECT id, title, endpoint, severity, cve, description, sensor
        FROM vulnerabilities
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Step 1: Group by endpoint and exact CVE match
        grouped_data = defaultdict(list)
        for row in rows:
            key = (row["endpoint"], row["cve"])
            grouped_data[key].append(row)

        # Step 2: Similarity-based grouping
        final_groups = {}
        group_id = 1

        for (endpoint, _), vulnerabilities in grouped_data.items():
            if len(vulnerabilities) == 1:
                # Assign a unique group for single vulnerabilities
                final_groups[f"group_{group_id}"] = vulnerabilities
                group_id += 1
            else:
                # Perform text similarity-based clustering
                texts = [f"{v['title']} {v['description']}" for v in vulnerabilities]

                # Generate TF-IDF matrix
                vectorizer = TfidfVectorizer()
                tfidf_matrix = vectorizer.fit_transform(texts)

                # Reduce dimensions with SVD
                svd = TruncatedSVD(n_components=min(50, tfidf_matrix.shape[1]), random_state=42)
                reduced_matrix = svd.fit_transform(tfidf_matrix)

                # Apply DBSCAN clustering
                dbscan = DBSCAN(eps=0.5, min_samples=2, metric="cosine")
                clusters = dbscan.fit_predict(reduced_matrix)

                # Assign clusters
                cluster_map = defaultdict(list)
                for idx, cluster_label in enumerate(clusters):
                    if cluster_label == -1:
                        # Treat outliers as a separate group
                        cluster_label = group_id
                        group_id += 1
                    cluster_map[cluster_label].append(vulnerabilities[idx])

                # Add clusters to final groups
                for cluster_label, cluster_items in cluster_map.items():
                    group_key = f"group_{group_id}"
                    final_groups[group_key] = cluster_items
                    group_id += 1

        # Format response
        result = []
        for group, items in final_groups.items():
            for item in items:
                result.append({
                    "title": item["title"],
                    "endpoint": item["endpoint"],
                    "tag": group,
                    "severity": item["severity"],
                    "cve": item["cve"],
                    "description": item["description"],
                    "sensor": item["sensor"]
                })

        cursor.close()
        connection.close()
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

