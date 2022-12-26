FROM tensorflow/tensorflow:latest-gpu

WORKDIR /spectre-code

RUN pip install -U jupyterlab pandas matplotlib numpy
RUN mkdir dataset

EXPOSE 8888

ENTRYPOINT ["jupyter", "lab","--ip=0.0.0.0","--allow-root","--no-browser"]