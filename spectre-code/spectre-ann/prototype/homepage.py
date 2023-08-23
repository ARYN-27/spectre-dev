import streamlit as st
import pandas as pd
import sqlite3
import time
from confluent_kafka.admin import AdminClient
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
from streamlit import date_input
from datetime import datetime
import plotly.express as px
import altair as alt
from auth import create_users_table, add_user, verify_password, user_exists

# Connect to the SQLite database
db_path = "database/predictions.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create the users table if it doesn't exist
create_users_table()

# Add a sample user (you can also create a registration form)
if not user_exists("admin"):
    add_user("admin", "admin")


st.set_page_config(
    page_title="SPECTRE DDoS Detection Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Login form
def login_page():
    # dashboard title
    st.title("🧠 SPECTRE DASHBOARD")
    st.caption("A lightweight solution for DDoS Detection")
    st.divider()
    #st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if verify_password(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username  
        else:
            st.sidebar.error("Invalid username or password")

    account_expander = st.expander(label='User Guide')
    with account_expander:
        colored_header(
            label="Welcome to Spectre. Let's get started",
            description="A guide to setting up SPECTRE",
            color_name="yellow-80",
        )
        st.markdown("""
            Thank you for choosing our app! This user manual will guide you through the process of changing file locations, starting the app, and accessing the web UI. Let's get started:

            ## 1. Change File Locations in the Docker Compose
            - Locate and open the `docker-compose.yml` file in a text editor.
            - Under the `volumes` section, replace the folder location with the location of your choosing. For example, `<local file directory>:/prototype`.
            - Modify the file locations as needed to ensure that the files are saved in the desired locations. Make sure to use absolute paths or relative paths that are correct within the Docker context.
            - Save the changes to the Docker Compose file.

            ## 2. Start the App
            - Make sure you have Docker installed on your machine. If not, you can download it from the [official website](https://www.docker.com/get-started).
            - Open your terminal and navigate to the directory where the app is located.
            - Type `docker compose up -d` and hit enter. This command will start the app in detached mode, allowing it to run in the background.

            ## 3. Access the Web UI with the Provided IP Address and Port
            - Once the app is up and running, open your web browser.
            - In the address bar, enter the IP address of the machine where the app is running, followed by `:8501`. For example, if the IP address is `192.168.1.100`, you would type `http://192.168.1.100:8501`.
            - Press enter to access the web UI of the app.

            Congratulations! You have successfully changed the file locations, started the app, and accessed the web UI. If you encounter any issues or have any questions, please refer to the app's documentation.
            """)
# User Register Page
def register_user():
    #st.subheader("Register a new user")
    username = st.text_input("Enter a username")
    password = st.text_input("Enter a password", type="password")
    confirm_password = st.text_input("Confirm password", type="password")
    register_button = st.button("Register")

    if register_button:
        if password != confirm_password:
            st.error("Passwords do not match")
        elif user_exists(username):
            st.error("Username already exists")
        else:
            add_user(username, password)
            st.success("User registered successfully")


# Function to fetch data from the database and display it
def display_predictions():
    
    # Define Kafka configuration
    kafka_conf = {
        'bootstrap.servers': 'kafka:9092'
    }

    # Create an AdminClient instance
    admin_client = AdminClient(kafka_conf)

    # Get the metadata for the Kafka cluster
    metadata = admin_client.list_topics(timeout=10)

    #st.header("DASHBOARD")
        
    # Query the predictions from the database
    c.execute('SELECT * FROM predictions')
    predictions = c.fetchall()

    # Convert the predictions to a pandas DataFrame
    predictions_df = pd.DataFrame(predictions, columns=['ID', 'Prediction', 'Result', 'F1 Score', 'Timestamp'])
    #st.write(f"Unique values in Result column: {predictions_df['Result'].unique()}")

    # Convert the Timestamp column to a DatetimeIndex
    #anomaly_counts = predictions_df[predictions_df['Result'] == 'ANOMALY'].set_index('Timestamp').resample('5T').count()
        
    # Convert the 'Timestamp' column to a pandas datetime object
    predictions_df['Timestamp'] = pd.to_datetime(predictions_df['Timestamp'])
        
    # Set the 'Timestamp' column as the index and resample
    # Group the predictions_df by 'Result' and resample by 'Timestamp'
    grouped_df = predictions_df.groupby('Result').resample('5T', on='Timestamp').count()

    # Filter the grouped_df for 'ANOMALY' and reset the index
    anomaly_counts = grouped_df.loc['ANOMALY'].reset_index()

            
    # Query the count of anomalies and benign results from the database
    c.execute("SELECT Result, COUNT(*) FROM predictions GROUP BY Result")
    count_data = dict(c.fetchall())
    #st.write(f"Total rows in predictions table: {len(predictions)}")  # Add this line to check the values in the Result column

    #st.divider()
        
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
        style_metric_cards(background_color="#191923", border_left_color= "#E59500", border_color="#E59500", border_size_px=2, border_radius_px= 5)
        
    with col_top2:
        #st.subheader("SPECTRE Details")
        colored_header(
            label="SPECTRE Details",
            description="Overview on SPECTRE",
            color_name="yellow-80",
        )
        kafka_expander = st.expander(label='KAFKA METRICS')
        with kafka_expander:
            #st.subheader("Welcome to Developer Area")
            # Kafka Information
            st.write("KAFKA METRICS")  
            # Create a container to display the number of topics
            with st.container():
                # Check if there are any errors
                if not metadata.brokers:
                    st.warning("Kafka is not running properly!")
                else:
                    st.success("Kafka is running properly!")
        status_expander = st.expander(label='SPECTRE Status')
        with status_expander:
            #st.write("SPECTRE Status")
            st.write("Version: 2.0")

    st.divider()
        
    # Add the date_input widget to the date_col
    selected_date = date_input("Select a Date", value=datetime.today().date())
        
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
                        
        # Add a 'Date' column to the anomaly_counts DataFrame
        anomaly_counts['Date'] = anomaly_counts['Timestamp'].dt.date


        # Filter the anomaly_counts DataFrame based on the selected date
        anomaly_counts_filtered = anomaly_counts[anomaly_counts['Date'].astype(str) == str(selected_date)]
            
        #st.write("Anomaly Counts Filtered DataFrame:")
            
        if anomaly_counts_filtered.empty:
            st.warning("No data available for the selected date.")
        else:
            fig = px.line(anomaly_counts_filtered, x='Timestamp', y='ID', title='Anomalies Over Time')
            fig.update_xaxes(title_text='Timestamp')
            fig.update_yaxes(title_text='Anomaly Count')
            st.plotly_chart(fig, use_container_width=True)


def dashboard_page():
    # Add a collapsible sidebar for the refresh button
    with st.sidebar:
        #st.title(f"Loggged in as {st.session_state.username}")
        st.header("🧠 SPECTRE Options")
        #st.write("Click the button below to refresh the data:")
        st.caption("Refresh SPECTRE Dashboard")
        refresh_button = st.button("Refresh Data")
        st.divider()
        st.subheader("⚠️ DANGEROUS")
        st.caption("Careful when using these options")
        del_db = st.button("Delete Database Entry")
        # Add a divider and logout button
        st.divider()
        st.subheader("🚪 Log Out")
        logout_button = st.button("Logout")
    
    # Check if the logout button is clicked
    if logout_button:
        st.session_state.logged_in = False
        login_page()
        return
       
    # dashboard title
    st.title("🧠 SPECTRE DASHBOARD")
    st.header(f"Hello, {st.session_state.username}")
    st.caption("A lightweight solution for DDoS Detection")

    # Create a placeholder for the line chart
    line_chart_placeholder = st.empty()
    
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Account Management", "Developer Options"])
    
    with tab1:
        display_predictions()
        # Refresh the data when the refresh button is clicked
        if refresh_button or del_db:
            if refresh_button:
                display_predictions()
            elif del_db:
                # Delete all rows from the predictions table
                c.execute("DELETE FROM predictions")
                conn.commit()
                
    with tab2:    
        account_expander = st.expander(label='Register Account')
        with account_expander:
            colored_header(
                label="Register User",
                description="Register new users",
                color_name="yellow-80",
            )
            register_user()
    with tab3:
        dev_expander = st.expander(label='Developer Area')
        with dev_expander:
            st.header("Welcome to Developer Area")
            st.caption("Feature to be added")


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    dashboard_page()