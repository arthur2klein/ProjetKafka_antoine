from confluent_kafka import Producer
from global_land_mask import globe
import json
import time
import random
import numpy as np
import os
import logging

ip = os.environ.get("ip")
logging.basicConfig(level=logging.INFO)

def delivery_report(err, msg):
    if err is not None:
        logging.error(f'Échec de la livraison du message : {err}')
    else:
        logging.info(f'Message livré à {msg.topic()} [{msg.partition()}]')

def wait_for_kafka(number_of_tries, time_between_tries):
  time.sleep(time_between_tries)
  for _ in range(10):
    try:
      res = Producer({'bootstrap.servers': "kafka:9092"})
      res.produce('test', key=ip, value='banane', callback=delivery_report)
      return res
    except Exception as e:
      print(f'Error when connectiong to Kafka: {e}')
      time.sleep(2)
  raise TimeoutError('kafka did not answer.')

# Configuration du producteur Kafka
logging.info("Creation of the producer")
producer = wait_for_kafka(
    number_of_tries = 10,
    time_between_tries = 2
)
logging.info("Producer created")

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
    logging.info(f"Sending {data}")
    while globe.is_ocean(data["latitude"],data["longitude"]):
        data = {
            'ip': ip,
            'latitude': latitude + (random.randrange(-10,10)/10),
            'longitude': longitude + (random.randrange(-10,10)/10),
            'timestamp': time.time()
        }
        logging.info(f'Sending data: {data}')

    producer.produce('coordinates', value=json.dumps(data), callback=delivery_report)
    producer.poll(0)

# Boucle pour envoyer des données GPS de manière continue
while True:

    logging.info(f'Topics available: {producer.list_topics()}')
    send_gps_data(ip)
    time.sleep(3)  # Pause de 5 secondes entre les envois
