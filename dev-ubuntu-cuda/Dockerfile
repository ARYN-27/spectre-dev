#-----------------------------------------------------------------------------------------------------------------------
# https://gitlab.com/nvidia/container-images/cuda/-/blob/master/dist/11.7.1/ubuntu2204/devel/cudnn8/Dockerfile
#-----------------------------------------------------------------------------------------------------------------------

FROM nvidia/cuda:11.2.1-devel-ubuntu20.04 as base
ENV DEBIAN_FRONTEND noninteractive

#The working directory for the containers is /spectre-code
WORKDIR /spectre-code


RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip

RUN apt-get install -y curl gnupg wget git git-lfs software-properties-common build-essential libgl1

#Create a directory "dataset" to mount the datasets later
RUN mkdir dataset

#-----------------------------------------------------------------------------------------------------------------------
#   NVIDIA ENVIRONMENT SETTING
#   https://gitlab.com/nvidia/container-images/cuda/-/raw/master/dist/11.2.1/ubuntu2004/devel/cudnn8/Dockerfile
#-----------------------------------------------------------------------------------------------------------------------

FROM base as base-amd64

ENV NV_CUDNN_VERSION 8.1.1.33
ENV NV_CUDNN_PACKAGE_NAME "libcudnn8"

ENV NV_CUDNN_PACKAGE "libcudnn8=$NV_CUDNN_VERSION-1+cuda11.2"
ENV NV_CUDNN_PACKAGE_DEV "libcudnn8-dev=$NV_CUDNN_VERSION-1+cuda11.2"


#FROM base as base-arm64

#ENV NV_CUDNN_VERSION 8.1.1.33
#ENV NV_CUDNN_PACKAGE_NAME "libcudnn8"

#ENV NV_CUDNN_PACKAGE "libcudnn8=$NV_CUDNN_VERSION-1+cuda11.2"
#ENV NV_CUDNN_PACKAGE_DEV "libcudnn8-dev=$NV_CUDNN_VERSION-1+cuda11.2"

FROM base-${TARGETARCH}

ARG TARGETARCH

LABEL maintainer "NVIDIA CORPORATION <cudatools@nvidia.com>"
LABEL com.nvidia.cudnn.version="${NV_CUDNN_VERSION}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    ${NV_CUDNN_PACKAGE} \
    ${NV_CUDNN_PACKAGE_DEV} \
    && apt-mark hold ${NV_CUDNN_PACKAGE_NAME} \
    && rm -rf /var/lib/apt/lists/*

#-----------------------------------------------------------------------------------------------------------------------
#   INSTALLING TENSORFLOW
#-----------------------------------------------------------------------------------------------------------------------

#RUN curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /home/Miniconda3-latest-Linux-x86_64.sh

#RUN /home/miniconda/bin/conda create --name tf python=3.9

#RUN /home/miniconda/bin/conda deactivate

#RUN /home/miniconda/bin/conda activate tf

#RUN /home/miniconda/bin/conda install -c conda-forge cudatoolkit=11.2 cudnn=8.1.0

#RUN export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/

RUN pip install --upgrade pip

RUN pip install tensorflow-gpu

#------------------------------------------------------------------------------------------------------------------------
#   INSTALL JUPYTERLAB and requirements
#-----------------------------------------------------------------------------------------------------------------------

RUN pip install -U jupyterlab pandas matplotlib scipy ipywidgets keras h5py

#-----------------------------------------------------------------------------------------------------------------------
#   JUPYTER EXTENSIONS
#-----------------------------------------------------------------------------------------------------------------------

RUN jupyter nbextension enable --py widgetsnbextension

# JupyterLab Extensions
RUN pip install -U jupyterlab-tensorboard-pro
RUN pip install -U ipympl
RUN pip install -U jupyterlab-system-monitor
RUN pip install -U jupyterlab-git
RUN pip install -U jupyterlab-horizon-theme
RUN pip install -U jupyterlab_materialdarker
RUN pip install -U jupyterlab_execute_time
RUN pip install -U jupyterlab_nvdashboard
RUN pip install -U black
RUN pip install -U isort
RUN pip install jupyterlab-code-formatter

#-----------------------------------------------------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------------------------------------------------

#RUN chown -R admin:admin /content
#RUN chmod -R 777 /content
#RUN chown -R admin:admin /home
#RUN chmod -R 777 /home

#USER admin

#-----------------------------------------------------------------------------------------------------------------------
#   STARTING JUPYTERLAB
#-----------------------------------------------------------------------------------------------------------------------

#Expose port 8888 for JupyterLab
EXPOSE 8888

# Start JupyterLab with root and no broswer spawn
ENTRYPOINT ["jupyter", "lab","--ip=0.0.0.0","--allow-root","--no-browser","--ResourceUseDisplay.track_cpu_percent=True"]