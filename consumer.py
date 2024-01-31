from confluent_kafka import Consumer
import json
import psycopg2
import time

def wait_for_availability(function_that_fails, number_of_tries, time_between_tries):
  for _ in range(number_of_tries):
    try:
      res = function_that_fails()
      return res
    except:
      time.sleep(time_between_tries)
  raise TimeoutError(f'{function_that_fails.__name__} did not answer.')

# Connexion à PostgreSQL
conn = wait_for_availability(
    lambda:psycopg2.connect(dbname='gps_db', user='utilisateur', password='kafkacestcool', host='db'),
    number_of_tries = 10,
    time_between_tries = 2
)
cursor = conn.cursor()

# Configuration du consommateur Kafka
consumer = wait_for_availability(lambda:Consumer({
        'bootstrap.servers': "kafka-broker:9092",
        'group.id': "gps_consumer_group",
        'auto.offset.reset': 'earliest'  # Commence à lire depuis le début du topic
    }),
    number_of_tries = 10,
    time_between_tries = 2
)
consumer.subscribe(['coordinates'])

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break

        data = json.loads(msg.value())
        cursor.execute(
            "INSERT INTO gps_data (ip, latitude, longitude, timestamp) VALUES (%s, %s, %s, %s)",
            (data['ip'], data['latitude'], data['longitude'], data['timestamp'])
        )
        conn.commit()

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
    conn.close()

