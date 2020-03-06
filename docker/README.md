# Docker testing

## Directory Contents

`Dockerfile` -- build recipe using a Centos:8 base image

`rillgen2d.c` -- base code for compiling with `gcc`

Build the Docker container

```
git clone https://github.com/jdpellet/rillgen2d
cd rillgen2d/docker
docker build -t rillgen2d:centos .
```

Run the container locally

```
docker run -it -v $(pwd):/work -w /work rillgen2d:centos 
```

`rillgen2d` requires two input files in the current working directory, `input.txt` -- the parameter file, and `topo.txt` the digital elevation model (DEM). A sample DEM is hosted here: https://data.cyverse.org/dav-anon/iplant/home/tswetnam/rillgen2d
