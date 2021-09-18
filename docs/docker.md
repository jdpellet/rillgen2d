## Docker Desktop (Windows)

Rillgen2d has been containerized using a full remote desktop with XPRA

It can be run from Docker Desktop on a localhost port address which is accessed via the browser. 

### Build from Source

Use the `main` branch

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
docker run -it --rm -v /home/$USER/Downloads/:/inputs -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY rillgen2d:latest
```
