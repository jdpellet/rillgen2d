# rillgen2d

Predicts where rills/gullies will occur on a real or proposed landscape as a function of topography, climate, and cover characteristics.

# Installation

## Dependencies

`rillgen2d` is written in [C](https://en.wikipedia.org/wiki/C_(programming_language)), but uses geospatial data input layers, such as [GeoTiff](https://www.ogc.org/standards/geotiff). These require open-source geospatial software packages such as [GDAL](https://gdal.org/), [GEOS](https://trac.osgeo.org/geos), and [PROJ](https://proj.org/) to manage their projection information. The Graphic User Inferface (GUI) is written in [Python3](https://www.python.org/) using [Tkinter](https://docs.python.org/3/library/tkinter.html).

### Prerequisites

Regardless of Operating System, we suggest you install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (recommended) or full [Anaconda](https://www.anaconda.com/products/individual) prior to running the scripts below. The Docker option does not require conda installation. 


### Setup on Windows 10 

We have tested these options for running the platform on Windows 10.

[ImageMagick](https://imagemagick.org/script/download.php#windows) -- the ImageMagick package is not available in Windows `conda` package management, which handles the other dependencies.

Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

Run the [Miniconda installer](https://docs.conda.io/en/latest/miniconda.html)

Download the current repository to your computer.

Open the Conda terminal, change directory to the `rillgen2d` installation folder.

```
cd C:\path\to\rillgen2d
```

##### Set up the conda environment

Run the following commands to create adn activate the conda enviornment
```
# create environment for rillgen2d
conda env create -f env_streamlit_windows.yml

# activate conda environment
conda activate rillgen2d
```

##### Run the Rillgen2d GUI
Requires: Conda, ImageMagick, rillgen2d conda env.
Once the Python environment has been created and activated, you can start the GUI from the Terminal or Command Prompt:

```
streamlit run rillgen2dApp.py
```

#### Run with Docker Desktop (Windows)

Install the [Windows Subsystem for Linux (WSL) v2.0](https://docs.microsoft.com/en-us/windows/wsl/install-win10) installation with the [Ubuntu flavor](https://ubuntu.com/wsl) and enable it.

Install [Docker Desktop for Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows)

**note: does not require conda installation**

Download the image from [DockerHub](https://hub.docker.com/u/tswetnam/rillgen2d) `tswetnam/rillgen2d:latest` tag

The image is very large - because it contains an entire remote desktop in addition to miniconda and the rillgen2d conda environment (geospatial packages). 

Run the image and open the Optional Settings and select Local Host Port - the container runs port `9876` but you can select any port you choose.

Select a Host Path - this is necessary to ensure that the data you input and output from Rillgen will be saved back to your host. 

Select a Container Path - the host folder will be renamed inside the container; suggest loading into the `/home/user/workspace` folder name. When you run rillgen, you can look for that `workspace` folder.

Open in Browser - select the open in browser option once the container is running. The remote desktop can also be found at `localhost:<port>` that you defined in the Host Port setting.

#### Run from Windows Subsystem for Linux

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

#### Download Source Code

The RillGen2D uses a combination of opensource python libraries for visualization in the Graphic User Interface (GUI). To install these tools we recommend that you use the `conda` environment and package manager. 

First, download the latest `.zip` or `.tar.gz` from our [Releases](https://github.com/tyson-swetnam/rillgen2d/releases)

[Source Code Windows v0.3 zip](https://github.com/tyson-swetnam/rillgen2d/archive/refs/tags/0.3.zip)

[Source Code Linux/MaOSX v0.2 zip](https://github.com/tyson-swetnam/rillgen2d/archive/refs/tags/0.2.zip)

[Source Code Linux/MacOSX v0.2 tar.gz](https://github.com/tyson-swetnam/rillgen2d/archive/refs/tags/0.2.tar.gz)

Next, unpack the Zip or Tar file and put them somewhere you can find them from the command prompt or terminal. 


If you want to pull from source, clone this repository to your local computer:

```
git clone https://github.com/jdpellet/rillgen2d
cd rillgen2d
```

The `main` branch has the latest features. The `develop` branch is where testing is taking place. 

## Debugging

```
# check your python version (should be +3.7.*)
python3 --version
```

If `conda` has errors, you may need to add it to the PATH, or set up the `~/.bashrc` and `~/bash_profile` for your user in Cygwin

Set the `conda` path to wherever you installed it - in linux, this is typically in `/opt` in Windows it may be in `C:/cygwin64/miniconda/`

```
echo ". /home/${USER}/miniconda3/etc/profile.d/conda.sh" >> ~/.bashrc
echo "conda activate base" >> ~/.bashrc
source ~/.bashrc
```

We provide an example `bash_profile` in the `/test` sub-folder in this repository.

You can add the following for Cygwin, this will correct any errors around `\r` 

```
#  IMPORTANT - Ignore carriage returns when using a Cygwin environment.
export SHELLOPTS
set -o igncr
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
## Create Streamlit version of the Rillgen2d app.

To get it running (on Mac and Linux, havent worked with windows yet), you'll need to do the following (assuming you already have conda installed)

```
 conda env create -f ./environment_linux.yml
 conda activate rillgen2d

 cd ./streamlit/streamlit_app_dir

# This is to fix an issue with the app moving to the temp directory and messing up the relative import. Not actually necessary if you don't encounter an error
 
 export PYTHONPATH=$PYTHONPATH:$(PWD)/rillgen2d.py
 streamlit run app.py
 ```
