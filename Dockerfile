#Container is based on latest Tensorflow image
FROM tensorflow/tensorflow:latest-gpu 

#The working directory for the containers is /spectre-code
WORKDIR /spectre-code

#Install requirements
RUN pip install -U jupyterlab pandas matplotlib
#Create a directory "dataset" to mount the datasets later
RUN mkdir dataset
#Install npm & nodejs for jupyter-lab extensions
RUN apt install nodejs npm

#Expose port 8888 for JupyterLab
EXPOSE 8888

ENTRYPOINT ["jupyter", "lab","--ip=0.0.0.0","--allow-root","--no-browser"]
#ENTRYPOINT [ "jupyter-lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]