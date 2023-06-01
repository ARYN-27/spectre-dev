# anomalay_detector.py
# https://www.phind.com/search?cache=cf139efb-38e8-4fb5-9cda-5c67194a11a6

from confluent_kafka import Consumer, Producer, KafkaError
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import time
from rich.console import Console
from rich.table import Table



# Print the header for the anomaly detector module
print("==================================")
print("SPECTRE - CONSUMER & ANOMALY DETECTOR MODULE")
print("==================================")
time.sleep(1)

# Load the pre-trained TensorFlow model
model = load_model('/home/aryn/spectre-dev/spectre-code/spectre-ann/Model/DDOS_2/A/spectre_ddos_2_h5.h5')

# Print the header for the anomaly detector module
consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'mygroup',
    'session.timeout.ms': 6000,
    'auto.offset.reset': 'earliest',
    'queued.min.messages': 1  # Add this line to set the minimum number of records in the queue to 1
}

# Create a Kafka consumer instance
consumer = Consumer(consumer_conf)

# Define Kafka producer configuration for handshake with the consumer
handshake_producer_conf = {
    'bootstrap.servers': 'localhost:9092'
}

# Create a Kafka producer instance for handshake
handshake_producer = Producer(handshake_producer_conf)
handshake_producer.produce('handshake', 'READY')

# Define Kafka consumer configuration for handshake with the producer
handshake_consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'consumer_handshake_group',
    'session.timeout.ms': 6000,
    'auto.offset.reset': 'earliest'
}

# Create a Kafka consumer instance for handshake
handshake_consumer = Consumer(handshake_consumer_conf)
handshake_consumer.subscribe(['handshake'])

# Initialize timeout counter and limit for handshake
timeout_counter = 0
timeout_limit = 10

# Perform handshake with the producer
while True:
    msg = handshake_consumer.poll(1.0)
    if msg is None:
        timeout_counter += 1
        if timeout_counter >= timeout_limit:
            print("==================================")
            print("CONNECTION FAILURE")
            print("==================================")
            exit(1)
        continue
    if msg.error():
        print(f"Handshake consumer error: {msg.error()}")
    else:
        handshake_msg = msg.value().decode('utf-8')
        if handshake_msg == 'READY':
            print("==================================")
            print("CONNECTION ESTABLISHED")
            print("==================================")
            break

# Subscribe to the 'detect_anomalies' topic
consumer.subscribe(['detect_anomalies'])

# Initialize the data buffer
received_data_buffer = []

# Initialize the predictions lis
predictions_list = []

# Rich Output
console = Console()


# Consume messages and process them using the on_message function
def on_message(msg):
    global received_data_buffer
    
    threshold = 0.65  # Set the threshold value for anomaly detection
    
    if msg.error():
        print(f"Consumer error: {msg.error()}")
    else:
        received_data_str = msg.value().decode('utf-8')  # Convert the received data to a string
        received_data_list = received_data_str.strip('[]').split(',')  # Convert the received data string to a list of strings using comma as the delimiter
        received_data_buffer.append(received_data_list)  # Append the list of strings to the buffer

        if len(received_data_buffer) == 7:
            X_received = np.array(received_data_buffer, dtype=np.float64)  # Convert the buffer to a numpy array of floats
            prediction = model.predict(X_received, verbose=0)
            #print(f'Prediction: {prediction}')
            
            # Detection Table
            # Create a table for the prediction output
            table = Table(title="Detection")
            table.add_column("Prediction")
            table.add_column("Result")
            
            # Check if there is an anomaly and print the appropriate message
            if np.any(prediction > threshold):
                #print("==================================")
                #print("ANOMALY")
                #print("==================================")
                result = "ANOMALY"
            else:
                #print("==================================")
                #print("BENIGN")
                #print("==================================")
                result = "BENIGN"
            
            #for pred in prediction:
            table.add_row(str(prediction), result)
                
            console.print(table)
                        
            received_data_buffer = []  # Reset the buffer
            #predictions_list.append(prediction) # Append the prediction to the predictions_list
        else:
            # Debug: Print the received_data_str length
            #print(f"Received data length: {len(received_data_str)}")  
            
            # Debug: Print the received_data_buffer
            print(f"Received data instances: {len(received_data_buffer)}") 
            
            
# Start the Live context manager and consume messages
while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print(f"Consumer error: {msg.error()}")
    else:
        on_message(msg) 