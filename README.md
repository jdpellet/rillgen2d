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

```
# update conda
conda update -n base -c defaults conda

# remove old rillgen2d environment
conda remove --name rillgen2d --all

# create new environment for rillgen2d
conda env create -f environment.yml

# activate conda environment
conda activate rillgen2d

# update conda environment 
conda env update --prefix ./env --file environment.yml  --prune
```

### Starting the GUI

Once the appropriate Python environment has been created, you can start the GUI

```
# check your python version (should be 3.7.*)
python --version

# start the UI
python rillgen2d.py
```

## Docker

Alternately, you can run the entire program with [Docker]()
