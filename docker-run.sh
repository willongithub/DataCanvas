OS=$(uname)

if [ "$OS" = "Linux" ]; then
## For Linux Host
    xhost + local:docker

    docker run --rm \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        datacanvas-3.10

    xhost - local:docker

elif [ "$OS" = "Darwin" ]; then
## For Darwin Host (bug not resolved)
    IP=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
    DISPLAY=$IP:0

    xhost + $IP

    docker run --rm \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        datacanvas-3.10

    xhost - $IP

else
## For Windows Host
    DISPLAY=$(ipconfig | grep IPv4 | awk '{print $NF}' | awk 'FNR <= 1') 

    docker run --rm \
        -e DISPLAY=$DISPLAY:0 \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        datacanvas-3.10
fi