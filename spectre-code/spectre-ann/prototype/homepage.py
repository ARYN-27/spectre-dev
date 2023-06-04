import streamlit as st
import pandas as pd
import sqlite3
import time

# Connect to the SQLite database
db_path = "/home/aryn/spectre-dev/spectre-code/spectre-ann/database/predictions.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

st.set_page_config(
    page_title="SPECTRE DDoS Detection Dashboard",
    page_icon="🧠",
    layout="wide",
)

# Add a style block with the link to the Google font
st.write("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&display=swap');
        body {
            font-family: 'Fira Code', monospace;
        }
        h1 {
            font-family: 'Fira Code', monospace;
        }
        .metric-name, .metric-value {
            font-family: 'Fira Code', monospace;
        }
    </style>
""", unsafe_allow_html=True)

# dashboard title
st.title("SPECTRE DASHBOARD")

# Function to fetch data from the database and display it
def display_predictions():
    # Query the predictions from the database
    c.execute('SELECT * FROM predictions')
    predictions = c.fetchall()

    # Convert the predictions to a pandas DataFrame
    predictions_df = pd.DataFrame(predictions, columns=['ID', 'Prediction', 'Result'])
    #st.write(f"Unique values in Result column: {predictions_df['Result'].unique()}")


    # Create a new DataFrame for the line chart with separate columns for anomalies and benign predictions
    line_chart_data = predictions_df.pivot_table(index='ID', columns='Result', values='Prediction', aggfunc='count').fillna(0)

    # Query the count of anomalies and benign results from the database
    c.execute("SELECT Result, COUNT(*) FROM predictions GROUP BY Result")
    count_data = dict(c.fetchall())
    #st.write(f"Total rows in predictions table: {len(predictions)}")  # Add this line to check the values in the Result column

    # Create a row for the metrics
    metrics_row = st.columns(2)

    # Display the count of anomalies and benign results using st.metric
    with metrics_row[0]:
        st.metric("Anomaly Count", count_data.get('ANOMALY', 0))
    with metrics_row[1]:
        st.metric("Benign Count", count_data.get('BENIGN', 0))

    # Create two columns for displaying the table and line chart side by side
    col1, col2 = st.columns(2)

    # Display the table in the first column
    with col1:
        # Add a select box to choose between top 10 results and all results
        table_option = st.selectbox("Choose table display option:", ["Top 10 Results", "All Results"])

        # Filter the DataFrame based on the selected option
        if table_option == "Top 10 Results":
            display_df = predictions_df.tail(10)
        else:
            display_df = predictions_df

        # Display the table with a scrollable container
        st.write(display_df.style.set_properties(subset=['ID', 'Prediction', 'Result'], **{'text-align': 'center'})
                 .set_table_styles([dict(selector='th', props=[('text-align', 'center')])])
                 .hide_index(), height=400)

    # Display the line chart in the second column
    with col2:
        st.write("This line chart shows the number of anomalies and benign predictions over time:")
        st.line_chart(line_chart_data)

# Refresh the data every 2 minutes (120 seconds)
while True:
    display_predictions()
    time.sleep(120)
