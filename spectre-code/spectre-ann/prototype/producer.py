# consumer.py
# https://www.phind.com/search?cache=cf139efb-38e8-4fb5-9cda-5c67194a11a6

from confluent_kafka import Producer, Consumer, KafkaError
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelBinarizer
from sklearn.decomposition import PCA

# ... (keep the code for data preprocessing)
def prod_datapreprocess(csv_file):
    df = pd.read_csv(csv_file)
    
    dimensions_num_for_PCA = 7

    def clean_dataset(df):
        assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"
        df.dropna(inplace=True)
        indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(axis=1)
        return df[indices_to_keep]

    def get_PCA_feature_names(num_of_pca_components):
        feature_names = []
        for i in range(num_of_pca_components):
            feature_names.append(f"Principal component {i+1}")
        return feature_names
    
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    df_cleaned = df.copy()
    df_cleaned = clean_dataset(df_cleaned)

    df_cleaned = df_cleaned.reset_index()
    df_cleaned.drop('index', axis=1, inplace=True)

    # Saving the label attribute before dropping it
    df_labels = df_cleaned['label']
    df_cleaned.drop('label', axis=1, inplace=True)
    df_features = df_cleaned.columns.tolist()

    df_scaled = StandardScaler().fit_transform(df_cleaned)
    df_scaled = pd.DataFrame(data=df_scaled, columns=df_features)

    # Performing PCA
    pca = PCA(n_components=dimensions_num_for_PCA)
    principal_components = pca.fit_transform(df_scaled)

    # Creating a DataFrame with principal components
    principal_component_headings = get_PCA_feature_names(dimensions_num_for_PCA)
    df_pc = pd.DataFrame(data=principal_components, columns=principal_component_headings)

    df_final = pd.concat([df_pc, df_labels], axis=1)

    lb = LabelBinarizer()
    df_final['label'] = lb.fit_transform(df_final['label'])

    X = df_final.drop(['label'], axis = 1)
    y = df_final['label']

    return X

X = prod_datapreprocess('/home/aryn/spectre-dev/dataset/CICIDS2017/MachineLearningCSV/MachineLearningCVE/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv')


#scaler = StandardScaler()
#X_scaled = scaler.fit_transform(X)

#separator = np.array([-1], dtype=np.float32) 

producer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'max.in.flight.requests.per.connection': 1   # Add this line to set the maximum number of in-flight messages to 1
}

producer = Producer(producer_conf)


# Handshake with the consumer
handshake_consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'producer_handshake_group',
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

# Send a ready message to the consumer
producer.produce('handshake', 'READY')

# ... (keep the code for sending the scaled data to the Kafka producer line by line)

for i, row in X.iterrows():
    #serialized_data = str(row)  # Convert the row to a string
    serialized_data = ','.join(map(str, row.values))
    print(f"Serialized data: {serialized_data}")
    producer.produce('detect_anomalies', serialized_data)

producer.flush()
