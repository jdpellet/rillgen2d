[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip) [![license](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://opensource.org/licenses/GPL-3.0) 

# rillgen2d

Code, example data, and manuscript supplemental materials which accompany **Pelletier, JD, XXX**

Author: [Jon D Pelletier](http://jdpellet.github.io/) [![](https://orcid.org/sites/default/files/images/orcid_16x16.png)](http://orcid.org/0000-0002-0702-2646)

Software Developers: [Jacob van der Leeuw](https://jvanderleeuw) [![](https://orcid.org/sites/default/files/images/orcid_16x16.png)](http://orcid.org/0000-0003-0892-9837), Elliot Hagyard  

UX Testing: [Tyson Lee Swetnam](https://tyson-swetnam.github.io/) [![](https://orcid.org/sites/default/files/images/orcid_16x16.png)](http://orcid.org/0000-0002-6639-7181)

## Contents

The repository is organized (in the attempt) to enable reproducible research as part of the [FAIR data principles](https://www.go-fair.org/fair-principles/).

You can (re)run these analyses using your own computer, on commercial cloud, or a data science workbench [CyVerse](https://cyverse.org) Discovery Environment.

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