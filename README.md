# rillgen2d
Predicts where rills/gullies will occur on a real or proposed landscape as a function of topography, climate, and cover characteristics

# Installation

## Dependencies

Rillgen2D is written in C, but uses geospatial input layers, such as geoTiff files. These require open-source geospatial software packages such as GDAL, GEOS, and PROJ to manage their projection information. The Graphic User Inferface (GUI) is written in Python using Tkinter.

### Installing with Conda or mini-Conda

We have provided a `requirements.txt` file which can be used with Conda to install the stack.

```
conda create --name rillgen2d_env pip
pip install -r requirements.txt
```

## Docker

Alternately, you can run the entire program using Docker.
