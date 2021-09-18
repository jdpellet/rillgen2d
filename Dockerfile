FROM harbor.cyverse.org/vice/xpra/ubuntu:20.04

USER root

# Install applications we need
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        g++ \
        gcc \
        git \
        mesa-utils \
        libgl1-mesa-dev \
        libgl1-mesa-glx \
        libxcomposite-dev \
        libxcursor1 \
        libxi6 \
        libxtst6 \
        libxss1 \
        libpci-dev \
        libasound2

# Create Rillgen2d conda environment
RUN cd && mkdir rillgen2d
COPY input.txt rillgen2d/
COPY console.py rillgen2d/
COPY rillgen2d.py rillgen2d/
COPY rillgen2d.c rillgen2d/
COPY environment_linux.yml rillgen2d/

# create conda environment for rillgen2d
RUN conda update -n base -c defaults conda -y && \
    cd rillgen2d && \
    conda env create -f environment_linux.yml

RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate rillgen2d" >> ~/.bashrc

ENV DISPLAY=:0

WORKDIR rillgen2d
