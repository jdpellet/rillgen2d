FROM gitpod/workspace-full-vnc

USER root

# Install MiniConda and Tini
ENV TZ=US/Phoenix
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone
ENV LANG=C.UTF-8 
ENV LC_ALL "en_US.UTF-8"

ENV PATH /opt/conda/bin:$PATH

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git mercurial subversion

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc

RUN apt-get install -y curl grep sed dpkg && \
    TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
    dpkg -i tini.deb && \
    rm tini.deb && \
    apt-get clean

RUN chown -R 33333:33333 /opt/conda

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
