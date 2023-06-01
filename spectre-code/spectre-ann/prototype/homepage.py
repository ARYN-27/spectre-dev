import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import h5py

st.set_page_config(
    page_title="SPECTRE DDoS Detection Dashboard",
    page_icon="🧠",
    layout="wide",
)

# dashboard title
st.title("SPECTRE DASHBOARD")

# Dashboard Consumer 
#dashboard_consumer_conf = {
#    'bootstrap.servers': 'localhost:9092',
#    'group.id': 'dashboard_consumer_group',
#    'auto.offset.reset': 'earliest'
#}

#dashboard_consumer = Consumer(dashboard_consumer_conf)
#dashboard_consumer.subscribe(['results'])


results_placeholder = st.empty()

# Read the data from the HDF5 file
filename = '/home/aryn/spectre-dev/spectre-code/spectre-ann/prototype/kafka_output/predictions.h5'
with h5py.File(filename, 'r') as hdf:
    predictions_data = hdf['predictions'][:]
predictions_df = pd.DataFrame(predictions_data, columns=['prediction'])

# Display the data in Streamlit
results_placeholder.dataframe(predictions_df)
