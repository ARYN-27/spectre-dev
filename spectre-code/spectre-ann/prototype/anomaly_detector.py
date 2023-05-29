from confluent_kafka import Consumer, Producer, KafkaError
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

# ... (keep the code for data preprocessing and Kafka consumer initialization)

# Load the pre-trained TensorFlow model
model = load_model('/home/aryn/spectre-dev/spectre-code/spectre-ann/Model/DDOS_2/A/spectre_ddos_2_h5.h5')

consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'mygroup',
    'session.timeout.ms': 6000,
    'auto.offset.reset': 'earliest',
    'queued.min.messages': 1  # Add this line to set the minimum number of records in the queue to 1
}

consumer = Consumer(consumer_conf)

# Handshake with the producer
handshake_producer_conf = {
    'bootstrap.servers': 'localhost:9092'
}

handshake_producer = Producer(handshake_producer_conf)
handshake_producer.produce('handshake', 'READY')

handshake_consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'consumer_handshake_group',
    'session.timeout.ms': 6000,
    'auto.offset.reset': 'earliest'
}

handshake_consumer = Consumer(handshake_consumer_conf)
handshake_consumer.subscribe(['handshake'])

while True:
    msg = handshake_consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print(f"Handshake consumer error: {msg.error()}")
    else:
        handshake_msg = msg.value().decode('utf-8')
        if handshake_msg == 'READY':
            break


consumer.subscribe(['detect_anomalies'])

received_data_buffer = []

def on_message(msg):
    global received_data_buffer
    if msg.error():
        print(f"Consumer error: {msg.error()}")
    else:
        received_data_str = msg.value()  # Convert the received data to a string
        if received_data_str == b'\x80\x02':  # Check if received_data_str is the separator
            print(f"Received data buffer length: {len(received_data_buffer)}")  # Debug: Print the buffer length
            if len(received_data_buffer) == 7:
                X_received = received_data_buffer
                prediction = model.predict(X_received)
                print(f'Prediction: {prediction}')
            else:
                print("Unexpected data length, skipping this message")
            received_data_buffer = []  # Reset the buffer
        else:
            print(f"Received data length: {len(received_data_str)}")  # Debug: Print the received_data_str length
            received_data_buffer.append(received_data_str)

# Consume messages and process them using the on_message function
while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print(f"Consumer error: {msg.error()}")
    else:
        on_message(msg)