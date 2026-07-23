
<img src="https://gitlab.com/computational-discovery-research/calopy/-/raw/main/src/calopy/assets/AdditionalFiles/CalopyGraphicalAbstract.png" alt="CalopyGraphicalAbstract"/>

# Calopy — An Advanced Framework for the Integration and Analysis of Indirect Calorimetry Data

![Python >= 3.9](https://img.shields.io/badge/Python-%3E%3D3.9-green?logo=python&logoColor=white) 
![Docker](https://img.shields.io/badge/Docker-Supported-blue?logo=docker&logoColor=white) 
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

---

Calopy is an innovative software suite for the intuitive and comprehensive analysis of indirect calorimetry data. Calopy is an open-source, web-based Shiny for Python application, accessible online or locally, platform-independent, and available via any web browser.  

##### Launch the app here:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[https://calopy.app](https://calopy.app)
##### User guide:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; [Calopy_HOWTO.pdf](https://gitlab.com/computational-discovery-research/calopy/-/blob/main/Calopy_HOWTO.pdf)

<br>

---


### Setup the latest release version of the app locally:

<br>

#### Option 1: direct local installation
```bash
### 1. download Calopy repository in current folder and unzip
curl https://gitlab.com/computational-discovery-research/calopy/-/archive/release/calopy-release.zip -o calopy-release.zip && unzip -q calopy-release.zip && rm calopy-release.zip  && mv calopy-release calopy

### 2. install Python >=3.9: https://www.python.org/downloads/

### 3. install required Python packages
pip install -r ./calopy/src/requirements.txt

### 4. go into subdirectory and run the app
cd ./calopy/src
shiny run --reload --port 8180 --launch-browser ./app.py

### 5. open browser and go to: http://localhost:8180/
```

<br>

#### Option 2. using a virtual environment (recommended)
```bash
### 1. download Calopy repository in current folder and unzip
curl https://gitlab.com/computational-discovery-research/calopy/-/archive/release/calopy-release.zip -o calopy-release.zip && unzip -q calopy-release.zip && rm calopy-release.zip  && mv calopy-release calopy

### 2. install conda or mamba: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html

### 3. create a new environment with necessary packages
conda env create --file ./calopy/src/conda_environment.yml

### 4. activate calopy environment
conda activate calopy

### 5. go into subdirectory and run the app
cd ./calopy/src
shiny run --reload --port 8180 --launch-browser ./app.py

### 6. open browser and go to: http://localhost:8180/
```

<br>

#### Option 3: using Docker
```bash
### 1. install docker following the steps here: https://www.docker.com/

### 2. pull lastest Calopy image
docker pull loipf/calopy:latest

### 3. start the container
docker run -p 8180:8180 loipf/calopy:latest

### 4. open browser and go to: http://localhost:8180/
```

<br>

---

#### Reference:  

Loipfinger S, Grosholz M, Kumar S, Erbilir H, Dyar KA, Müller TD, Grein S, Rozman J, Klingenspor M, Meyer C, Lutter D. Calopy — An Advanced Framework for the Integration and Analysis of Indirect Calorimetry Data. *Nature Metabolism*, 2025. <br />
DOI: [https://doi.org/10.1038/s42255-025-01316-8](https://doi.org/10.1038/s42255-025-01316-8)

---

Calopy is released under the [MIT License](https://gitlab.com/computational-discovery-research/calopy/-/blob/main/LICENSE).



