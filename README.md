# rillgen2d: Predicting Rill and Gully Erosion

**rillgen2d** is a software package that predicts the locations of rills and gullies on landscapes, considering factors like topography, climate, and vegetation. This tool aids in understanding and mitigating soil erosion risks.

**Authors:**

* **Creator:** [Jon D Pelletier](https://www.geo.arizona.edu/Pelletier){target=_blank}
* **Software Engineers:** Jacob van der Leeuw, Elliot Hagyard
* **UX Testers:** [Tyson Swetnam](https://tysonswetnam.com){target=_blank}

### Installation

While `rillgen2d` is written in C, it leverages geospatial data formats like GeoTIFF, requiring software like GDAL, GEOS, and PROJ for projection management. The user interface is built with Python 3 and Streamlit.

**Prerequisites:**

- **Miniconda/Anaconda:** We recommend installing Miniconda or Anaconda for managing dependencies.

**Installation Methods:**

**Windows 10:**

1. **Install Script (Recommended):**
    
    - Download the repository and locate the `scripts\install_windows.bat` file.
    
    - Run the script. It will guide you through installing Miniconda and setting up the conda environment.
    
    - After installation, open the Anaconda Prompt, activate the environment with `conda activate rillgen2d`, navigate to the project folder, and run the application using `python run.py`.
    
    - Access the GUI at http://localhost:5000 in your browser.
  
2. **Manual Installation:**
    
    - Install Miniconda and download the repository.
    
    - Open the Anaconda Prompt, navigate to the project folder, and create/activate the environment:
        
        ```powershell
        conda env create -f environment_windows.yml
        conda activate rillgen2d
        ```
    
    - Launch the application with `python run.py` and access the GUI at http://localhost:5000.

**Linux and Mac OS X:**

1. Open a terminal and create/activate the environment:
   
    ```bash
    conda env create -f environment_linux.yml
    #conda env create -f environment_macos.yml
    conda activate rillgen2d
    ```

2. Start the GUI: 

    ```bash
    python run.py
    ```

**Docker:** (Coming Soon)

### Download Source Code

- Release versions are available on the [Releases](https://github.com/tyson-swetnam/rillgen2d/releases) page.

- To clone the repository:
    ```bash
    git clone https://github.com/jdpellet/rillgen2d
    cd rillgen2d
    ```

Current version is maintained on `main` branch

### Debugging Tips

- Ensure you're using Python 3.11 or later: `python3 --version`

- If environment creation is slow, consider using `mamba`:
  
    ```bash
    conda install -n base mamba
    mamba env create -f environment_windows.yml  
    
    # (or environment_linux.yml)
    # (or environment_macos.yml)
    ```

**Note:** On Linux, parameter values might display with a newline character (`\n`). This is expected behavior, and you should leave it as is while updating values.
Use code with caution.