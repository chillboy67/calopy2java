
FROM ubuntu:22.04


### system packages 
RUN apt-get update && apt-get install -yq curl wget jq vim bzip2 libglib2.0-0
RUN apt-get install -y binutils libc6 libc-bin 

### install miniconda to /miniconda
RUN curl -LO "https://repo.anaconda.com/miniconda/Miniconda3-py312_25.1.1-2-Linux-x86_64.sh" && \
    bash Miniconda3-py312_25.1.1-2-Linux-x86_64.sh -p /miniconda -b && \
    rm Miniconda3-py312_25.1.1-2-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}

### install calopy packages
RUN pip install -r https://gitlab.com/computational-discovery-research/calopy/-/raw/release/src/requirements.txt

### download code and unzip
RUN curl -L https://gitlab.com/computational-discovery-research/calopy/-/archive/release/calopy-release.tar.gz -o calopy-release.tar.gz && \
    tar -xzf calopy-release.tar.gz && rm calopy-release.tar.gz && \
    mv calopy-release calopy

WORKDIR ./calopy/src 
EXPOSE 8180
ENTRYPOINT ["shiny", "run", "--reload", "--port", "8180", "--host", "0.0.0.0", "./app.py"]

