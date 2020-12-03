# rillgen2d
Predicts where rills/gullies will occur on a real or proposed landscape as a function of topography, climate, and cover characteristics

# Installation

Clone this repository to your local computer

```
git clone https://github.com/jdpellet/rillgen2d
cd rillgen2d
```

## Dependencies

`rillgen2d` is written in [C](), but uses geospatial data input layers, such as [GeoTiff](). These require open-source geospatial software packages such as [GDAL](), [GEOS](), and [PROJ]() to manage their projection information. The Graphic User Inferface (GUI) is written in [Python3]() using [Tkinter]().

### Installing with Conda or mini-Conda

We have provided a `environment.yml` file which can be used with [Conda]() to install the stack.

```
# update conda
conda update -n base -c defaults conda
# create environment for rillgen2d
conda env create -f environment.yml
# activate conda environment
conda activate rillgen
```

### Starting the GUI

Once the appropriate Python environment has been created, you can start the GUI

```
python rillgen2d.py
```

## Docker

Alternately, you can run the entire program with Docker
