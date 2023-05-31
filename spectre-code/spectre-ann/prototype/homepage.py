import streamlit as st
import streamlit_authenticator as stauth


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

