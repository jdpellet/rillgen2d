FROM continuumio/miniconda3:4.9.2
ENV TZ=US/Phoenix
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone
# Install applications we need
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-gdal \
        gdal-bin   \
        libgdal-dev  \
        gcc \
        g++ \
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
COPY . /root/
RUN conda update -n base -c defaults conda -y && \
    cd root && \
    conda env create -f environment_linux.yml
# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "rillgen2d", "/bin/bash", "-c"]
WORKDIR /root
ENTRYPOINT ["conda", "run", "-n", "rillgen2d", "python", "rillgen2d.py"]