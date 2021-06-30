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

# copy contents of repo below this folder
COPY .. /opt/rillgen2d

# create conda environment for rillgen2d
RUN conda update -n base -c defaults conda -y && \
    cd /opt/rillgend2d && \
    conda env create -f environment_linux.yml

# enters conda environment for rillgen2d commands
SHELL ["conda", "run", "-n", "rillgen2d", "/bin/bash", "-c"]

WORKDIR /opt/rillgen2d

ENTRYPOINT ["conda", "run", "-n", "rillgen2d", "python3", "rillgen2d.py"]