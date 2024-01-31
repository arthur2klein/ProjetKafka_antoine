from confluent_kafka import Consumer
import json
import psycopg2

# Connexion à PostgreSQL
conn = psycopg2.connect(dbname='gps_db', user='utilisateur', password='kafkacestcool', host='db')
cursor = conn.cursor()

# Configuration du consommateur Kafka
consumer = Consumer(
    {
        'bootstrap.servers': "kafka-broker:9092",
        'group.id': "gps_consumer_group",
        'auto.offset.reset': 'earliest'  # Commence à lire depuis le début du topic
    }

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

