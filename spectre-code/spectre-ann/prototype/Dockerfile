FROM python:3.9-slim-bullseye
# Use arm64v8 for Raspberry Pi Deployment
#FROM arm64v8/python:3.9-slim-bullseye 

# Set the working directory
WORKDIR /prototype

# Copy the requirements.txt file into the container
COPY requirements.txt .

RUN pip3 install --upgrade pip

# Install any necessary dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the Kafka server port and Streamlit port
EXPOSE 9092

# Copy the producer.py and anomaly_detector.py files into the container
#COPY producer.py .

#COPY anomaly_detector.py .

# Run producer.py and anomaly_detector.py
CMD ["sh", "-c", "python producer.py & python anomaly_detector.py"]