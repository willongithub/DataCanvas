### For Linux Host
# xhost +

# docker run --rm \
#     -e DISPLAY=$DISPLAY \
#     -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
#     datacanvas-3.10

# xhost -


### For Darwin Host (bug not resolved)
# DISPLAY=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}') 

# xhost + DISPLAY

# docker run --rm \
#     -e DISPLAY=$DISPLAY:0 \
#     -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
#     datacanvas-3.10

# xhost - DISPLAY


### For Windows Host
DISPLAY=$(ipconfig | grep IPv4 | awk '{print $NF}' | awk 'FNR <= 1') 

docker run --rm \
    -e DISPLAY=$DISPLAY:0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    datacanvas-3.10