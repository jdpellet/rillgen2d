# rillgen2d

Predicts where rills/gullies will occur on a real or proposed landscape as a function of topography, climate, and cover characteristics.

## Installation

### Dependencies

`rillgen2d` is written in [C](https://en.wikipedia.org/wiki/C_(programming_language)), but uses geospatial data input layers, such as [GeoTiff](https://www.ogc.org/standards/geotiff). These require open-source geospatial software packages such as [GDAL](https://gdal.org/), [GEOS](https://trac.osgeo.org/geos), and [PROJ](https://proj.org/) to manage their projection information. The Graphic User Inferface (GUI) is written in [Python3](https://www.python.org/) using [Streamlit](https://streamlit.io/).

### Prerequisites

Regardless of Operating System, we suggest you install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (recommended) or full [Anaconda](https://www.anaconda.com/products/individual) prior to running the scripts below. The Docker option does not require conda installation.

## Setup on Windows 10

We have tested these options for running the platform on Windows 11.

### Run the install script

1. The first step is to download repository and open the repository in your file explorer.

2. Run the install script.
   * The script (scripts\install_windows.bat) downloads the miniconda installer, prompts the user to install conda, then creates the conda environment.
   * To run the installer, click on `install_windows.bat` in the Windows file explorer.

3. Windows will create a pop-up saying that they prevented the installer from running. To run it anyways, click "More info" and then click "Run Anyway".

4. After a short period, the Miniconda installer will prompt you about the different install options (the default options are fine for running rillgen).

5. After installing Miniconda, the intstaller will create the enviornment. This takes around 10 minutes.
6. Once the installer is finished, the text provides a command you can enter in the Anaconda Prompt to navigate to the correct folder. Copy it, then press enter to close the window
7. To run rillgen, you need to do the following
   1. Then, search `Anaconda Prompt (miniconda3)` in the search box in the taskbar
   2. In Anaconda Prompt, run `conda activate rillgen2d`
   3. Navigate to rillgen2d folder (either with the copied command or manually)
   4. Launch the application with `python run.py` in the Anaconda Prompt
   5. Then, [search localhost:5000 on your preferred browser](http://localhost:5000/)

### Manual Installation

#### Install Miniconda

Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

Run the [Miniconda installer](https://docs.conda.io/en/latest/miniconda.html)

Download the current repository to your computer.

Open the Conda terminal, change directory to the `rillgen2d` installation folder.

```powershell
cd C:\path\to\rillgen2d
```

#### Set up the conda environment

Run the following commands to create adn activate the conda environment

```powershell
# Create a temporary conda env in which to install mamba (installing in base can run into permissions issues)
conda create -n base2 mamba -c conda-forge -y

# Activate the temporary environment
conda activate base2

# create environment for rillgen2d
mamba env create -f environment_windows.yml

# activate conda environment
mamba activate rillgen2d

# Remove the temp env (if you want)
conda env remove -n base2

```

If you have an existing conda env named rillgen2d, you can remove it with the following command

```powershell
# or remove old rillgen2d environment
conda remove --name rillgen2d --all

```

### Run the Rillgen2d GUI

Requires: Conda, ImageMagick, rillgen2d conda env.
Once the Python environment has been created and activated, you can start the GUI from the Terminal or Command Prompt:

```powershell

python run.py
# You will be prompted to create a streamlit account, you can just hit enter to skip this step
```

[Search localhost:5000 on your preferred browser](http://localhost:5000/)

#### Run with Docker Desktop (Windows)

TBA

### Run from Windows Subsystem for Linux

TBA

## Install for Linux and Mac OS X

We have provided two `environment.yml` files which can be used with [Conda](https://docs.conda.io/en/latest/) to install the stack on Linux and Mac OS X, or Windows10.

Make sure to add `conda` to your PATH ir variables.

Open a Terminal:

```bash

# create environment for rillgen2d
conda env create -f environment_linux.yml

# activate conda environment
conda activate rillgen2d
```

If you have an older installation of `conda` you may need to update

```bash

# update conda
conda update -n base -c defaults conda

# update conda existing environment 
conda env update --prefix ./env --file environment_linux.yml  --prune

# or remove old rillgen2d environment
conda remove --name rillgen2d --all
```

Once the appropriate Python environment has been created, you can start the GUI from the Terminal or Command Prompt:

``` bash

python run.py

```

## Download Source Code

The RillGen2D uses a combination of opensource python libraries for visualization in the Graphic User Interface (GUI). To install these tools we recommend that you use the `conda` environment and package manager.

First, download the latest `.zip` or `.tar.gz` from our [Releases](https://github.com/tyson-swetnam/rillgen2d/releases)

[Source Code Windows v0.3 zip](https://github.com/tyson-swetnam/rillgen2d/archive/refs/tags/0.3.zip)

[Source Code Linux/MaOSX v0.2 zip](https://github.com/tyson-swetnam/rillgen2d/archive/refs/tags/0.2.zip)

[Source Code Linux/MacOSX v0.2 tar.gz](https://github.com/tyson-swetnam/rillgen2d/archive/refs/tags/0.2.tar.gz)

Next, unpack the Zip or Tar file and put them somewhere you can find them from the command prompt or terminal.

If you want to pull from source, clone this repository to your local computer:

``` shell

git clone https://github.com/jdpellet/rillgen2d
cd rillgen2d

```

The `main` branch has the latest features. The `develop` branch is where testing is taking place.

## Debugging

```

# check your python version (should be +3.7.*)
python3 --version

```

If it is taking too long to create the conda environment, installing mamba can dramatically speed up the process.

```
# At this point you should already have installed conda
# Install mamba into the base env. The install can take a little bit (upwards of 5 minutes).
conda install -n base mamba
# Create the corresponding env, replacing conda with mamba.
# For example, if you are on windows, enter the command
mamba env create -f environment_windows.yml 
```

If you have an older installation of `conda` you may need to update

```
# update conda
conda update -n base -c defaults conda

# update conda existing environment 
conda env update --prefix ./env --file environment_linux.yml  --prune

# or remove old rillgen2d environment
conda remove --name rillgen2d --all
```

**Note: In Linux the Parameters tab number values may appear with a newline character `\n` at the end of their boxes, leave these present and update the values as needed.**

### Building a Docker container

TBA

### Docker run commands

TBA
