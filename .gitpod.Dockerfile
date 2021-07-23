FROM gitpod/workspace-full-vnc

USER root

# add gitpod user to UID 1000
RUN usermod -d /home/gitpod -u 1000 gitpod

# give gitpod sudo
RUN apt-get update && apt-get install -y sudo
RUN echo 'ALL ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER gitpod

FROM continuumio/miniconda3:4.9.2
ENV TZ=US/Phoenix
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone
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
