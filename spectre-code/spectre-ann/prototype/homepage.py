import streamlit as st
import pandas as pd
import sqlite3
import time
from confluent_kafka.admin import AdminClient
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
from streamlit import date_input
from datetime import datetime

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
    st.header("🧠 SPECTRE Options")
    #st.write("Click the button below to refresh the data:")
    st.caption("Refresh SPECTRE Dashboard")
    refresh_button = st.button("Refresh Data")
    st.divider()
    st.subheader("⚠️ DANGEROUS")
    st.caption("Careful when using these options")
    del_db = st.button("Delete Database Entry")
    
    
# dashboard title
st.title("🧠 SPECTRE DASHBOARD")
st.caption("A lightweight solution for DDoS Detection")

# Create a placeholder for the line chart
line_chart_placeholder = st.empty()

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

    # Query the count of anomalies and benign results from the database
    c.execute("SELECT Result, COUNT(*) FROM predictions GROUP BY Result")
    count_data = dict(c.fetchall())
    #st.write(f"Total rows in predictions table: {len(predictions)}")  # Add this line to check the values in the Result column

    st.divider()
    
    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
        #st.subheader("Attack Summary")
        colored_header(
            label="Attack Summary",
            description="A summary of attacks that occured",
            color_name="yellow-80",
        )
        # Create a row for the metrics
        #metrics_row = st.columns(2)
        
        # Display the count of anomalies and benign results using st.metric
        #with metrics_row[0]:
        #    st.metric("DDoS Count", count_data.get('ANOMALY', 0))
        #with metrics_row[1]:
        #    st.metric("Benign Count", count_data.get('BENIGN', 0))
        
        met_col1, met_col2 = st.columns(2)
        met_col1.metric(label="DDoS Count",value=count_data.get('ANOMALY', 0))
        met_col2.metric(label="Benign Count",value=count_data.get('BENIGN', 0))
        style_metric_cards(background_color="#000000", border_left_color= "#E59500", border_color="#CCCCCC", border_size_px=1, border_radius_px= 5)
        
    with col_top2:
        #st.subheader("SPECTRE Details")
        colored_header(
            label="SPECTRE Details",
            description="Overview on SPECTRE",
            color_name="yellow-80",
        )
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
        st.write("Version: 2.0")

    st.divider()
    
    # Create two columns for displaying the table and line chart side by side
    col1, col2 = st.columns(2)

    # Display the table in the first column
    with col1:
        #st.subheader("Log Details")
        colored_header(
            label="Log Details",
            description="Attack Logs",
            color_name="yellow-80",
        )
        
        # Add the date_input widget to the date_col
        selected_date = date_input("Select a date", value=datetime.today().date())

        # Filter the DataFrame based on the selected date
        filtered_df = predictions_df[predictions_df['Timestamp'].dt.date == selected_date]
        
        # Add a select box to choose between top 10 results and all results
        table_option = st.selectbox("Choose table display option:", ["Recent 10 Results", "All Results"])

        # Filter the DataFrame based on the selected option
        if table_option == "Recent 10 Results":
            #display_df = predictions_df.tail(10)
            display_df = filtered_df.tail(10)
        else:
            #display_df = predictions_df
            display_df = filtered_df

        # Set the option to display all columns without truncation
        pd.set_option('display.max_columns', None)

        # Display the table with a scrollable container and full width
        st.dataframe(display_df[['Timestamp', 'F1 Score', 'Result']], use_container_width=True, hide_index=True)

    # Line Chart Definition
    # Create a new DataFrame for the line chart with separate columns for anomalies and benign predictions
    #line_chart_data = predictions_df[predictions_df['Result'] == 'ANOMALY'].set_index('Timestamp').resample('5S').count()['Result']
    # Display the line chart in the second column
    with col2:
        #st.subheader("Attack Graph")
        #st.write("This line chart shows the number of anomalies over time:")
        colored_header(
            label="Attack Graph",
            description="This line chart shows the number of anomalies over time",
            color_name="yellow-80",
        )
        st.write(f"Number of rows in predictions_df where Result is ANOMALY: {len(predictions_df[predictions_df['Result'] == 'ANOMALY'])}")
        
        # Calculate the time range of the data and set an appropriate resampling frequency
        time_range = (predictions_df['Timestamp'].max() - predictions_df['Timestamp'].min()).days

        if time_range <= 1:
            resample_freq = '5Min'
        elif time_range <= 7:
            resample_freq = '1H'
        elif time_range <= 30:
            resample_freq = '1D'
        else:
            resample_freq = '1W'
        
        # Filter the DataFrame to only include rows where the 'Result' column is 'ANOMALY'
        anomaly_df = predictions_df[predictions_df['Result'] == 'ANOMALY']

        # Set the index to the 'Timestamp' column and resample the DataFrame using the calculated frequency
        anomaly_df = anomaly_df.set_index('Timestamp').resample(resample_freq)

        # Count the number of anomalies within each time bin
        anomaly_data = anomaly_df.count()['Result']

        # Plot the line chart using the updated `anomaly_data` object
        st.line_chart(anomaly_data)
    
    dev_expander = st.expander(label='Developer Area')
    with dev_expander:
        st.header("Welcome to Developer Area")
        st.caption("Components to added")
        
            
    
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
