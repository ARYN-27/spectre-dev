# anomaly_detector.py
# https://www.phind.com/search?cache=cf139efb-38e8-4fb5-9cda-5c67194a11a6

from confluent_kafka import Consumer, Producer, KafkaError
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import time
from rich.console import Console
from rich.table import Table
from rich.text import Text
import warnings
import os
import sqlite3
from sklearn.metrics import f1_score
import datetime


# Suppress Python warnings
warnings.filterwarnings("ignore")

# Suppress TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Database Setup/Connection
# Connect to the SQLite database at the specified location
db_path = "database/predictions.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create Table if not exists
c.execute('''
   CREATE TABLE IF NOT EXISTS predictions (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       prediction TEXT,
       result TEXT,
       f1_score TEXT,
       timestamp DATETIME
   )
''')

# Drop all values in the predictions table
# FOR DEBUGGING PURPOSE. COMMENT OUT WHEN IN PRODUCTION
#c.execute('DELETE FROM predictions')

conn.commit()

# Rich Output
console = Console()
#
# Print the header for the anomaly detector module
#console.print("==================================")
#print("SPECTRE - CONSUMER & ANOMALY DETECTOR MODULE")
#print("==================================")
# Create a Text object with the desired styling
text = Text("===================================\n",style="bold magenta")
text.append("SPECTRE - CONSUMER & ANOMALY DETECTOR MODULE\n",style="bold magenta")
text.append("===================================",style="bold magenta")
console.print(text)
time.sleep(1)

# Load the pre-trained TensorFlow model
model = load_model('model/spectre_ddos_2_h5.h5')

# Print the header for the anomaly detector module
consumer_conf = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'mygroup',
    'session.timeout.ms': 6000,
    'auto.offset.reset': 'earliest',
    'queued.min.messages': 1  # Add this line to set the minimum number of records in the queue to 1
}

# Create a Kafka consumer instance
consumer = Consumer(consumer_conf)

# Define Kafka producer configuration for handshake with the consumer
handshake_producer_conf = {
    'bootstrap.servers': 'kafka:9092'
}

# Create a Kafka producer instance for handshake
handshake_producer = Producer(handshake_producer_conf)
handshake_producer.produce('handshake', 'READY')

# Define Kafka consumer configuration for handshake with the producer
handshake_consumer_conf = {
    'bootstrap.servers': 'kafka:9092',
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


# Consume messages and process them using the on_message function
def on_message(msg):
    global received_data_buffer
    
    threshold = 0.7 # Set the threshold value for anomaly detection
    
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
            
            threshold = 0.6  # Set the threshold value for anomaly detection

            y_true = np.array([1, 1, 1, 1, 1, 1, 1])  # Set the true labels
            if np.any(prediction > threshold):
                y_pred = np.array([1, 1, 1, 1, 1, 1, 1])  # Set the predicted labels
                result = "ANOMALY"
            else:
                y_pred = np.array([0, 0, 0, 0, 0, 0, 0])  # Set the predicted labels
                result = "BENIGN"

            f1 = f1_score(y_true, y_pred)  # Calculate the F1 score
            
            # Detection Table
            # Create a table for the prediction output
            table = Table(title="Detection")
            table.add_column("Prediction")
            table.add_column("Result")
            table.add_column("F1 Score")
            
            table.add_row(str(prediction), result, str(f1))
                
            console.print(table)
                        
            received_data_buffer = []  # Reset the buffer
            
            # Insert the prediction, result and F1 score into the database
            c.execute('''
                INSERT INTO predictions (prediction, result, f1_score, timestamp) VALUES (?, ?, ?, ?)
            ''', (str(prediction), result, str(f1), current_time))
            conn.commit()
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