xhost +

docker run --rm \
    -u=$(id -u $USER):$(id -g $USER) \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v $(pwd):datacanvas/datacanvas \
    datacanvas-3.10

xhost -