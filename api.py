from fastapi import FastAPI
import psycopg2
from pydantic import BaseModel
import uvicorn
import time

def wait_for_availability(function_that_fails, number_of_tries, time_between_tries):
  for _ in range(number_of_tries):
    try:
      res = function_that_fails()
      return res
    except:
      time.sleep(time_between_tries)
  raise TimeoutError(f'{function_that_fails.__name__} did not answer.')

app = FastAPI()

# Modèle Pydantic pour les données GPS
class GPSData(BaseModel):
    ip: str
    latitude: float
    longitude: float
    timestamp: int

# Connexion à PostgreSQL
conn = wait_for_availability(
    lambda:psycopg2.connect(dbname='gps_db', user='utilisateur', password='kafkacestcool', host='db'),
    number_of_tries = 5,
    time_between_tries = 2
)
cursor = conn.cursor()

@app.get("/gps/{ip}", response_model=GPSData)
def get_gps_data(ip: str):
    cursor.execute("SELECT ip, latitude, longitude, timestamp_ FROM gps_data WHERE ip = %s ORDER BY timestamp_ DESC LIMIT 1", (ip,))
    row = cursor.fetchone()
    if row == None:
        return {}
    return GPSData(ip=row[0], latitude=row[1], longitude=row[2], timestamp=row[3])

uvicorn.run(app, host="0.0.0.0", port = 8080)
