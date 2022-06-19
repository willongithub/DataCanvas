# xhost +

# docker run --rm \
#     -e DISPLAY=$DISPLAY \
#     -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
#     datacanvas-3.10

# xhost -

LOCAL=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}') 

xhost + $LOCAL

docker run --rm \
    -e DISPLAY=$LOCAL:0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    datacanvas-3.10

xhost - $LOCAL