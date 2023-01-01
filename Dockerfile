#Container is based on latest Tensorflow image
FROM tensorflow/tensorflow:latest-gpu 

#The working directory for the containers is /spectre-code
WORKDIR /spectre-code

#pip upgrade
RUN pip install --upgrade pip

#Install requirements
RUN pip install -U jupyterlab pandas matplotlib

#Create a directory "dataset" to mount the datasets later
RUN mkdir dataset

# JupyterLab Extensions
RUN pip install jupyterlab-tensorboard-pro
RUN pip install ipympl
RUN pip install jupyterlab-system-monitor
#RUN pip install jupyterlab-git
RUN pip install jupyterlab-horizon-theme
RUN pip install jupyterlab_execute_time
RUN pip install jupyterlab_nvdashboard

#Expose port 8888 for JupyterLab
EXPOSE 8888

# Start JupyterLab with root and no broswer spawn
ENTRYPOINT ["jupyter", "lab","--ip=0.0.0.0","--allow-root","--no-browser"]
