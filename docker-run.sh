#!/bin/bash
docker run -it --rm \
-u=$(id -u $USER):$(id -g $USER) \
-e DISPLAY=$DISPLAY \
-v /tmp/.X11-unix:/tmp/.X11-unix:rw \
datacanvas-docker
/bin/bash
