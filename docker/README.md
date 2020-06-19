# Running Rillgen2d with Docker

change into a directory with the necessary `topo.txt` and `input.txt` files

Run Docker:

```
docker run -it -v ${PWD}:/data tswetnam/rillgen2d:latest
```

check for outputs

## Building `rillgen2d` with Docker (but to be run locally)

Contents: 

`Dockerfile` -- build recipe using `gcc`

`rillgen2d.c` -- base code for compiling with `gcc`

Build Rillgen2D as a Docker container

```
git clone https://github.com/jdpellet/rillgen2d
cd rillgen2d/docker
docker build -t rillgen2d:latest .
```

## Build Rillgen2D with Docker

You can build the C code locally by using `gcc` Docker

```
docker run --rm -v "$PWD":/usr/src/rillgen2d -w /usr/src/rillgen2d gcc:4.9 gcc -o rillgen2d rillgen2d.c -lm -g      
```

The `-lm` flags are required for the math, and `-g` is for debugging with `gdb`

After the `rillgen2d` is compiled you can run the algorithm. 

## Sample Data

IMPORTANT:`rillgen2d` requires two input files in the current working directory:

  * `input.txt` -- the parameter file
  * `topo.txt` the digital elevation model (DEM). 
  
A sample `topo.txt` DEM is hosted here: https://data.cyverse.org/dav-anon/iplant/home/tswetnam/rillgen2d
