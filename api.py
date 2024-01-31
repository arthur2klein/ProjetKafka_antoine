from fastapi import FastAPI
import psycopg2
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Modèle Pydantic pour les données GPS
class GPSData(BaseModel):
    ip: str
    latitude: float
    longitude: float
    timestamp: int

# Connexion à PostgreSQL
conn = psycopg2.connect(dbname='gps_db', user='utilisateur', password='kafkacestcool', host='db')
cursor = conn.cursor()

@app.get("/gps/{ip}", response_model=GPSData)
def get_gps_data(ip: str):
    cursor.execute("SELECT ip, latitude, longitude, timestamp_ FROM gps_data WHERE ip = %s ORDER BY timestamp_ DESC LIMIT 1", (ip,))
    row = cursor.fetchone()
    if row == None:
        return {}
    return GPSData(ip=row[0], latitude=row[1], longitude=row[2], timestamp=row[3])

uvicorn.run(app, host="0.0.0.0", port = 8080)
