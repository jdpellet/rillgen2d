FROM gitpod/workspace-full-vnc
FROM continuumio/miniconda3:4.9.2
ENV TZ=US/Phoenix
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone
    
RUN chown -R gitpod /opt/conda

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
