from confluent_kafka import Consumer, KafkaError
from datetime import datetime
import json
import psycopg2
import time
import logging

logging.basicConfig(level=logging.INFO)

def wait_for_psycopg2(number_of_tries, time_between_tries):
  for _ in range(10):
    try:
      res = psycopg2.connect(dbname='gps_db', user='utilisateur', password='kafkacestcool', host='db')
      return res
    except:
      time.sleep(2)
  raise TimeoutError('psycopg2 did not answer.')

def wait_for_kafka(number_of_tries, time_between_tries):
  for _ in range(10):
    try:
      res = Consumer({
          'bootstrap.servers': "kafka:9092",
          'group.id': "gps_consumer_group",
          'auto.offset.reset': 'earliest'  # Commence à lire depuis le début du topic
      })
      res.subscribe(['coordinates'])
      return res
    except:
      time.sleep(2)
  raise TimeoutError('kafka did not answer.')

# Connexion à PostgreSQL
conn = wait_for_psycopg2(
    number_of_tries = 10,
    time_between_tries = 2
)
cursor = conn.cursor()

# Configuration du consommateur Kafka
logging.info('Creation of the consumer')
consumer = wait_for_kafka(
    number_of_tries = 10,
    time_between_tries = 2
)
logging.info('Consumer created')

try:
    while True:
        logging.info(f'Topics available: {consumer.list_topics()}')
        consumer.subscribe(['coordinates'])
        msg = consumer.poll(timeout=1.0)
        logging.info(f'I received {msg}')
        if msg is None:
            logging.info(f'No message received')
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                logging.error(f'Error received: {msg.error()}')
                print(msg.error())
                continue

        try:
            data = json.loads(msg.value())
        except:
            logging.error(f'Error while converting {msg.value}')
            continue
        logging.info('Saving to database')
        cursor.execute(
            "INSERT INTO gps_data (ip, latitude, longitude, timestamp_) VALUES (%s, %s, %s, %s)",
            (data['ip'], data['latitude'], data['longitude'], datetime.fromtimestamp(data['timestamp']))
        )
        conn.commit()
        logging.info('Saved in database')

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
    conn.close()

