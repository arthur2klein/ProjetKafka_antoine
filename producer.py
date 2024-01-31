from confluent_kafka import Producer
from global_land_mask import globe
import json
import time
import random
import numpy as np
import os
ip = os.environ.get("ip")

# Configuration du producteur Kafka
producer = Producer(
    {
        'bootstrap.servers': "kakfa-broker:9092"
    }
)

# Coordonnées de Paris "Lieu de démarrage"
latitude = 48.87
longitude = 2.33 
def send_gps_data(ip):
    """
    Envoie des données GPS simulées au topic Kafka.
    """
    # Création de données GPS aléatoires
    data = {
        'ip': ip,
        'latitude': latitude + (random.randrange(-10,10)/10),
        'longitude':  longitude + (random.randrange(-10,10)/10),
        'timestamp': time.time()
    }
    while globe.is_ocean(data["latitude"],data["longitude"]):
        data = {
            'ip': ip,
            'latitude': latitude + (random.randrange(-10,10)/10),
            'longitude': longitude + (random.randrange(-10,10)/10),
            'timestamp': time.time()
        }
    # Envoi des données au topic 'coordinates'
        producer.produce('coordinates', key=ip, value=json.dumps(data), callback=delivery_report)
        producer.flush()

# Boucle pour envoyer des données GPS de manière continue
while True:
    send_gps_data(ip)
    time.sleep(3)  # Pause de 5 secondes entre les envois
