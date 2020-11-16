FROM continuumio/miniconda3
COPY . /home/rabasar
RUN pip install -r /home/rabasar/requirements.txt
RUN pip install /home/rabasar
RUN /bin/bash -c "conda -c conda-forge openblas tmux"

WORKDIR home/
