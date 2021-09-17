# rillgen2d
Predicts where rills/gullies will occur on a real or proposed landscape as a function of topography, climate, and cover characteristics

# Installation

## Dependencies

`rillgen2d` is written in [C](https://en.wikipedia.org/wiki/C_(programming_language)), but uses geospatial data input layers, such as [GeoTiff](https://www.ogc.org/standards/geotiff). These require open-source geospatial software packages such as [GDAL](https://gdal.org/), [GEOS](https://trac.osgeo.org/geos), and [PROJ](https://proj.org/) to manage their projection information. The Graphic User Inferface (GUI) is written in [Python3](https://www.python.org/) using [Tkinter](https://docs.python.org/3/library/tkinter.html).

#### Prerequisites

Regardless of Operating System, install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (recommended) or full [Anaconda](https://www.anaconda.com/products/individual) prior to running the scripts below. 

#### Download Source Code

The RillGen2D uses a combination of opensource python libraries for visualization in the Graphic User Interface (GUI). To install these tools we recommend that you use the `conda` environment and package manager. 

First, download the latest `.zip` or `.tar.gz` from our [Releases](https://github.com/tyson-swetnam/rillgen2d/releases)

[Source Code v0.1 zip](https://github.com/tyson-swetnam/rillgen2d/archive/refs/tags/0.1.zip)

[Source Code v0.1 tar.gz](https://github.com/tyson-swetnam/rillgen2d/archive/refs/tags/0.1.tar.gz)

Next, unpack the Zip or Tar file and put them somewhere you can find them from the command prompt or terminal. 


If ou want to pull from source, clone this repository to your local computer:

```
git clone https://github.com/jdpellet/rillgen2d
cd rillgen2d
```

The `main` branch has the latest features. The `develop` branch is where testing is taking place. 

### Setup on Windows 10 OS

We have tested these options for running the platform on Windows 10; note all options require the installation of [Miniconda](https://docs.conda.io/en/latest/miniconda.html) and [ImageMagick](https://imagemagick.org/script/download.php#windows) -- the ImageMagick package is not available in Windows `conda` package management, which handles the other dependencies. 

#### Cygwin

[Cygwin](https://www.cygwin.com/) is recommended.

Run the [Miniconda installer](https://docs.conda.io/en/latest/miniconda.html) select the Cygwin installation path for the miniconda

```
C:\cygwin64\home\your_username\miniconda
```

Select the 'add to path' option in the installation step.

Open the Cygwin terminal, change directory to the `rillgen2d` installation folder.

```
cd rillgen2d-main
```
##### create conda environment

run `conda` using the `environment_windows.yml` instead of `_linux.yml` file:

```
# create environment for rillgen2d
conda env create -f environment_windows.yml

# activate conda environment
conda activate rillgen2d
```

If `conda` has errors, you may need to add it to the PATH, or set up the `~/.bashrc` and `~/bash_profile` for your user in Cygwin


#### Example installation for Windows 10 

In Cygwin Terminal change into the directory where `rillgen2d` is kept.

```
cd rillgen2d-main
```

Install with `conda` using the `environment_windows.yml` instead of `_linux.yml` file.

```
# create environment for rillgen2d
conda env create -f environment_windows.yml

# activate conda environment
conda activate rillgen2d
```

Once the Python environment has been created, you can start the GUI from the Terminal or Command Prompt:

```
python3 rillgen2d.py
```

#### Windows Subsystem for Linux

TBA

[Windows Subsystem for Linux (WSL) v2.0](https://docs.microsoft.com/en-us/windows/wsl/install-win10) installation with the [Ubuntu flavor](https://ubuntu.com/wsl).

#### Run with Docker

TBA

#### Install for Linux and Mac OS X

We have provided two `environment.yml` files which can be used with [Conda](https://docs.conda.io/en/latest/) to install the stack on Linux and Mac OS X, or Windows10.

Make sure to add `conda` to your PATH environmental variables.

Open a Terminal:

```
# create environment for rillgen2d
conda env create -f environment_linux.yml

# activate conda environment
conda activate rillgen2d
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

Once the appropriate Python environment has been created, you can start the GUI from the Terminal or Command Prompt:

```
python3 rillgen2d.py
```

## Debugging

```
# check your python version (should be +3.7.*)
python3 --version
```

If `conda` has errors, you may need to add it to the PATH, or set up the `~/.bashrc` and `~/bash_profile` for your user in Cygwin

If you have an older installation of `conda` you may need to update

```
# update conda
conda update -n base -c defaults conda

# update conda existing environment 
conda env update --prefix ./env --file environment_linux.yml  --prune

# or remove old rillgen2d environment
conda remove --name rillgen2d --all
```

## Note:
On Linux in the Parameters Tab values may appear with a newline character '\n' at the end of their boxes, leave these present and update the values as needed.


### Building a Docker container

```
git clone https://github.com/jdpellet/rillgen2d
cd rillgen2d
docker build -t rillgen2d .
```

### Docker run commands:

On Linux:

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
