# SPECTRE (ANN based IDS)

## Setup Development Environment
- Use the Docker containers available in the repo:
    - Tensorflow Container: `dev-tensorflow`
    - Ubuntu 20.04 - Cuda Container: `dev-ubuntu-cuda`

## How to run the Code
1. Open the folder `prototype`
2. Run `docker compose up -d`
3. Access the Web UI at `http://<IP_Address>:8501/`

References: 
- [VGG-19 deep learning model trained using ISCX 2012 IDS Dataset](https://github.com/tamimmirza/Intrusion-Detection-System-using-Deep-Learning)
- [SafeML and Intrusion Detection Evaluation Dataset (CICIDS2017)](https://www.kaggle.com/code/kooaslansefat/cicids2017-safeml/notebook)
 

# User Manual

## 1. Change File Locations in the Docker Compose
- Locate and open the `docker-compose.yml` file in a text editor.
- Under the `volumes` section, replace the folder location with the location of your choosing. For example, `<local file directory>:/prototype`.

## 2. Start the App by Running `docker compose up -d`
- Run `docker compose up -d` and hit enter. This command will start the app in detached mode, allowing it to run in the background.

## 3. Access the Web UI with the Provided IP Address and Port
- Once the app is up and running, open your web browser.
- In the address bar, enter the IP address of the machine where the app is running, followed by `:8501`. For example, if the IP address is `192.168.1.100`, you would type `http://192.168.1.100:8501`.
- Press enter to access the web UI of the app.