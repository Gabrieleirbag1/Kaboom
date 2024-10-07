# This script manages the lifecycle of a Docker container named "kaboom-server".
# It provides functions to start the container in either detached or interactive mode,
# stop the container, and restart the container. The script accepts command-line arguments
# to determine the action to perform.

# Usage:
#   ./server_docker.sh [option]
#
# Options:
#   -it   Start the container in interactive mode.
#   -s    Stop the container if it is running.
#   -r    Restart the container.
#   (no option) Start the container in detached mode.
#
# The container is configured to map port 22222 on the host to port 22222 in the container.
# It also mounts the following directories and files from the host to the container:
#   - $(pwd)/Server to /app/Server
#   - $(pwd)/Dictionary to /app/Dictionary
#   - $(pwd)/requirements.txt to /app/requirements.txt
#
# The container image used is "kaboom-server:1.0".
#!/bin/bash

CONTAINER_NAME="kaboom-server"

start_detached() {
    sudo docker run -d --rm --name $CONTAINER_NAME -p 22222:22222 \
        -v $(pwd)/Server:/app/Server \
        -v $(pwd)/Dictionary:/app/Dictionary \
        -v $(pwd)/requirements.txt:/app/requirements.txt \
        kaboom-server:1.0
}

start_interactive() {
    sudo docker run -it --rm --name $CONTAINER_NAME -p 22222:22222 \
        -v $(pwd)/Server:/app/Server \
        -v $(pwd)/Dictionary:/app/Dictionary \
        -v $(pwd)/requirements.txt:/app/requirements.txt \
        kaboom-server:1.0
}

stop_container() {
    sudo docker stop $CONTAINER_NAME
}

restart_container() {
    stop_container
    start_detached
}

case "$1" in
    -it)
        start_interactive
        ;;
    -s)
        stop_container
        ;;
    -r)
        restart_container
        ;;
    *)
        start_detached
        ;;
esac