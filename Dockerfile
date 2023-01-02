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
RUN pip install -U jupyterlab-tensorboard-pro
RUN pip install -U ipympl
RUN pip install -U jupyterlab-system-monitor
#RUN pip install -U jupyterlab-git
RUN pip install -U jupyterlab-horizon-theme
RUN pip install -U jupyterlab_materialdarker
RUN pip install -U jupyterlab_execute_time
RUN pip install -U jupyterlab_nvdashboard
RUN pip install -U black
RUN pip install -U isort
RUN pip install jupyterlab-code-formatter

#Expose port 8888 for JupyterLab
EXPOSE 8888

# Start JupyterLab with root and no broswer spawn
ENTRYPOINT ["jupyter", "lab","--ip=0.0.0.0","--allow-root","--no-browser","--ResourceUseDisplay.track_cpu_percent=True"]
