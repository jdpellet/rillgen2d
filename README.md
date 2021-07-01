# rillgen2d
Predicts where rills/gullies will occur on a real or proposed landscape as a function of topography, climate, and cover characteristics

# Installation

Clone this repository to your local computer

```
git clone https://github.com/jdpellet/rillgen2d
cd rillgen2d
```

## Dependencies

`rillgen2d` is written in [C](https://en.wikipedia.org/wiki/C_(programming_language)), but uses geospatial data input layers, such as [GeoTiff](https://www.ogc.org/standards/geotiff). These require open-source geospatial software packages such as [GDAL](https://gdal.org/), [GEOS](https://trac.osgeo.org/geos), and [PROJ](https://proj.org/) to manage their projection information. The Graphic User Inferface (GUI) is written in [Python3](https://www.python.org/) using [Tkinter](https://docs.python.org/3/library/tkinter.html).

### Installing with Conda or mini-Conda

We have provided a `environment.yml` file which can be used with [Conda](https://docs.conda.io/en/latest/) to install the stack.

Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (recommended) or full [Anaconda](https://www.anaconda.com/products/individual) prior to running the scripts below.

#### Example install for Linux and Mac OS X

Open a Terminal:

```
# update conda
conda update -n base -c defaults conda

# update conda environments 
conda env update --prefix ./env --file environment_linux.yml  --prune

# or remove old rillgen2d environment
conda remove --name rillgen2d --all

# (re)create environment for rillgen2d
conda env create -f environment_linux.yml

# activate conda environment
conda activate rillgen2d
```

#### Example for Windows 10 

Open Command Prompt:

```
# update conda
conda update -n base -c defaults conda

# update conda environments 
conda env update --prefix ./env --file environment_windows.yml  --prune

# or remove old rillgen2d environment
conda remove --name rillgen2d --all

# (re)create environment for rillgen2d
conda env create -f environment_windows.yml

# activate conda environment
conda activate rillgen2d
```

To install on Windows, use the `environment_windows.yml` instead of `_linux.yml`

### Starting the GUI

Once the appropriate Python environment has been created, you can start the GUI from the Terminal or Command Prompt:

```
# check your python version (should be 3.9.*)
python3 --version

# start the UI
python3 rillgen2d.py
```

## Note:
On Linux in the Parameters Tab values may appear with a newline character '\n' at the end of their boxes, leave these present and update the values as needed.


## Docker

Alternately, you can run the program in [Docker](https://docker.com)

### Build 

```
git clone https://github.com/jdpellet/rillgen2d
cd rillgen2d
docker build -t rillgen2d .
```

### Docker run commands:

Linux:

use the volume flag to mount a folder with input data: `-e DISPLAY -v /home/<username/<data-folder>/:/inputs` 

```
# Install X11 server utils
sudo apt-get install x11-xserver-utils
# set display
export DISPLAY=:0
# allow X11
xhost +
# Run docker with host display settings and data volume
docker run -it --rm -v /home/tswetnam/Downloads/:/inputs -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY rillgen2d:latest
```
