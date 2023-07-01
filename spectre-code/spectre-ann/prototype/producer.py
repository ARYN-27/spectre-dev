# producer.py
# https://www.phind.com/search?cache=cf139efb-38e8-4fb5-9cda-5c67194a11a6

# Import necessary libraries
from confluent_kafka import Producer, Consumer, KafkaError
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelBinarizer
from sklearn.decomposition import PCA
import time
import warnings
from rich.console import Console
from rich.text import Text

# Suppress Python warnings
warnings.filterwarnings("ignore")

# Rich Output
console = Console()
 
# Print the welcome message
#print("==================================")
#print("SPECTRE - PRODUCER MODULE")
#print("==================================")
text = Text("===================================\n",style="bold magenta")
text.append("SPECTRE - PRODUCER MODULE\n",style="bold magenta")
text.append("===================================",style="bold magenta")
console.print(text)
time.sleep(1)



# Define a function to preprocess the data
def prod_datapreprocess(df, dimensions_num_for_PCA=7):
    
    # Read a CSV file and create a DataFrame
    #df = pd.read_csv(csv_file, chunksize=chunksize)
    
    dimensions_num_for_PCA = 7
    
    # Function to clean the dataset by removing NaN, inf, and -inf values
    def clean_dataset(df):
        assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"
        df.dropna(inplace=True)
        indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(axis=1)
        return df[indices_to_keep]

    # Function to get PCA feature names
    def get_PCA_feature_names(num_of_pca_components):
        feature_names = []
        for i in range(num_of_pca_components):
            feature_names.append(f"Principal component {i+1}")
        return feature_names
    
    # Preprocess the dataset
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    df_cleaned = df.copy()
    df_cleaned = clean_dataset(df_cleaned)

    df_cleaned = df_cleaned.reset_index()
    df_cleaned.drop('index', axis=1, inplace=True)

    # Saving the label attribute before dropping it
    df_labels = df_cleaned['label']
    df_cleaned.drop('label', axis=1, inplace=True)
    df_features = df_cleaned.columns.tolist()

    # Perform feature scaling
    df_scaled = StandardScaler().fit_transform(df_cleaned)
    df_scaled = pd.DataFrame(data=df_scaled, columns=df_features)

    # Performing PCA
    pca = PCA(n_components=dimensions_num_for_PCA)
    principal_components = pca.fit_transform(df_scaled)

    # Creating a DataFrame with principal components
    principal_component_headings = get_PCA_feature_names(dimensions_num_for_PCA)
    df_pc = pd.DataFrame(data=principal_components, columns=principal_component_headings)

    # Combine the principal components with the original labels
    df_final = pd.concat([df_pc, df_labels], axis=1)

    # Perform label binarization. Converts "ANOMALY" = 1 and "BENIGN" = 0.
    lb = LabelBinarizer()
    df_final['label'] = lb.fit_transform(df_final['label'])

    # Split the dataset into features (X) and labels (y)
    X = df_final.drop(['label'], axis = 1)
    y = df_final['label']

    # Returns features(X)
    return X


# Read the CSV file and preprocess the data

# DDoS Attack CSV
#X = prod_datapreprocess('/prototype/simulation_csv/Monday-WorkingHours.pcap_ISCX.csv')
#X = pd.read_csv('/prototype/simulation_csv/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv', chunksize=500)

# DDoS Prime CSV
#X = prod_datapreprocess('/prototype/simulation_csv/final_dataset.csv')
#X = pd.read_csv('/prototype/simulation_csv/final_dataset.csv', chunksize=500)

# Bening CSV
#X = prod_datapreprocess('/prototype/simulation_csv/Monday-WorkingHours.pcap_ISCX.csv')
#X = pd.read_csv('/prototype/simulation_csv/Monday-WorkingHours.pcap_ISCX.csv', chunksize=500)

# Prod CSV
#X = prod_datapreprocess('/prototype/simulation_csv/prod_csv.csv')
X = pd.read_csv('/prototype/simulation_csv/prod_csv.csv', chunksize=5000)

# Set the producer configuration
producer_conf = {
    'bootstrap.servers': 'kafka:9092',
    'max.in.flight.requests.per.connection': 1   # Add this line to set the maximum number of in-flight messages to 1
}

# Create a Kafka producer
producer = Producer(producer_conf)

# Set the handshake consumer configuration
handshake_consumer_conf = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'producer_handshake_group',
    'session.timeout.ms': 6000,
    'auto.offset.reset': 'earliest'
}

# Create a Kafka consumer for the handshake
handshake_consumer = Consumer(handshake_consumer_conf)
handshake_consumer.subscribe(['handshake'])

# Wait for the handshake from the consumer
timeout_counter = 0
timeout_limit = 50

# Perform handshake with the consumer
while True:
    # ... (Handshake waiting code)
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

# Send a ready message to the consumer
producer.produce('handshake', 'READY')

# Iterate through the preprocessed data and send it to the Kafka producer line by line
#for i, row in X.iterrows():
#    #serialized_data = str(row)  # Convert the row to a string
#    serialized_data = ','.join(map(str, row.values))
#    print(f"Serialized data: {serialized_data}")
#    producer.produce('detect_anomalies', serialized_data)
#    time.sleep(1.5)

# Iterate through the chunks of the CSV file
for chunk in X:
    # Preprocess the current chunk
    X = prod_datapreprocess(chunk)

    # Iterate through the preprocessed data and send it to the Kafka producer line by line
    for i, row in X.iterrows():
        serialized_data = ','.join(map(str, row.values))
        print(f"Serialized data: {serialized_data}")
        producer.produce('detect_anomalies', serialized_data)
        time.sleep(1.5)

# Flush the producer to ensure all messages are sent
producer.flush()
