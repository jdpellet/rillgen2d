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

# copy github repository
# RUN git clone https://github.com/tyson-swetnam/rillgen2d 

RUN mkdir rillgen2d

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

ENTRYPOINT ["conda", "run", "-n", "rillgen2d", "python3", "rillgen2d.py"]
