import streamlit as st
import pandas as pd
import sqlite3
import time
from confluent_kafka.admin import AdminClient
from st_on_hover_tabs import on_hover_tabs

# Connect to the SQLite database
db_path = "/home/aryn/spectre-dev/spectre-code/spectre-ann/prototype/database/predictions.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

st.set_page_config(
    page_title="SPECTRE DDoS Detection Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Add a collapsible sidebar for the refresh button
with st.sidebar:
#    st.header("🧠 SPECTRE Options")
#    #st.write("Click the button below to refresh the data:")
#    st.caption("Refresh SPECTRE Dashboard")
#    refresh_button = st.button("Refresh Data")
#    st.divider()
#    st.subheader("⚠️ DANGEROUS")
#    st.caption("Careful when using these options")
#    del_db = st.button("Delete Database Entry")
    
    
# dashboard title
st.title("🧠 SPECTRE DASHBOARD")
st.caption("A lightweight solution for DDoS Detection")


# Function to fetch data from the database and display it
def display_predictions():
    
    # Define Kafka configuration
    kafka_conf = {
        'bootstrap.servers': 'localhost:9092'
    }

    # Create an AdminClient instance
    admin_client = AdminClient(kafka_conf)

    # Get the metadata for the Kafka cluster
    metadata = admin_client.list_topics(timeout=5)

    #st.header("DASHBOARD")
       
    # Query the predictions from the database
    c.execute('SELECT * FROM predictions')
    predictions = c.fetchall()

    # Convert the predictions to a pandas DataFrame
    predictions_df = pd.DataFrame(predictions, columns=['ID', 'Prediction', 'Result', 'F1 Score', 'Timestamp'])
    #st.write(f"Unique values in Result column: {predictions_df['Result'].unique()}")

    # Convert the Timestamp column to a DatetimeIndex
    predictions_df['Timestamp'] = pd.to_datetime(predictions_df['Timestamp'])

    # Create a new DataFrame for the line chart with separate columns for anomalies and benign predictions
    line_chart_data = predictions_df[predictions_df['Result'] == 'ANOMALY'].set_index('Timestamp').resample('5S').count()['Result']

    # Query the count of anomalies and benign results from the database
    c.execute("SELECT Result, COUNT(*) FROM predictions GROUP BY Result")
    count_data = dict(c.fetchall())
    #st.write(f"Total rows in predictions table: {len(predictions)}")  # Add this line to check the values in the Result column

    st.divider()
    
    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
        st.subheader("Attack Summary")
        # Create a row for the metrics
        metrics_row = st.columns(2)
        
        # Display the count of anomalies and benign results using st.metric
        with metrics_row[0]:
            st.metric("DDoS Count", count_data.get('ANOMALY', 0))
        with metrics_row[1]:
            st.metric("Benign Count", count_data.get('BENIGN', 0))
    with col_top2:
        st.subheader("SPECTRE Details")
        # Kafka Information
        st.write("KAFKA METRICS")  
        # Create a container to display the number of topics
        with st.container():
            # Check if there are any errors
            if not metadata.brokers:
                st.warning("Kafka is not running properly!")
            else:
                st.success("Kafka is running properly!")
        st.write("SPECTRE Status")
        st.write("Version")

    st.divider()
    
    # Create two columns for displaying the table and line chart side by side
    col1, col2 = st.columns(2)

    # Display the table in the first column
    with col1:
        st.subheader("Log Details")
        # Add a select box to choose between top 10 results and all results
        table_option = st.selectbox("Choose table display option:", ["Recent 10 Results", "All Results"])

        # Filter the DataFrame based on the selected option
        if table_option == "Recent 10 Results":
            display_df = predictions_df.tail(10)
        else:
            display_df = predictions_df

        # Set the option to display all columns without truncation
        pd.set_option('display.max_columns', None)

        # Display the table with a scrollable container and full width
        st.dataframe(display_df[['Timestamp', 'F1 Score', 'Result']], use_container_width=True, hide_index=True)

    # Display the line chart in the second column
    with col2:
        st.subheader("Attack Graph")
        st.write("This line chart shows the number of anomalies over time:")
        st.line_chart(line_chart_data)
         
    
# Refresh the data when the refresh button is clicked
if refresh_button:
    display_predictions()
elif del_db:
    # Delete all rows from the predictions table
    c.execute("DELETE FROM predictions")
    conn.commit()
else:
    # Display the data automatically every 2 minutes (120 seconds)
    while True:
        display_predictions()
        time.sleep(120)
