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
# The container uses the host's network (--network host): it listens on port 22222 of the host
# and reaches the MQTT broker on the host's 127.0.0.1:1883 (live typing, issue #20).
# Secrets (KABOOM_MQTT_PASSWORD=...) go in a .env file next to this script, never in git.
# The TLS certificate of the game connections (#19) goes in Server/certs/, see docs/game-server-tls.md.
# It also mounts the following directories and files from the host to the container:
#   - $(pwd)/Server to /app/Server
#   - $(pwd)/Dictionary to /app/Dictionary
#   - $(pwd)/requirements.txt to /app/requirements.txt
#
# The container image used is "kaboom-server:1.1".
#!/bin/bash

CONTAINER_NAME="kaboom-server"
ENV_FILE=""
if [ -f "$(pwd)/.env" ]; then
    ENV_FILE="--env-file $(pwd)/.env"
else
    echo "No .env file: live typing (MQTT) will be off. See docs/mqtt-broker-setup.md"
fi

start_detached() {
    sudo docker run -d --rm --name $CONTAINER_NAME --network host $ENV_FILE \
        -v $(pwd)/Server:/app/Server \
        -v $(pwd)/Dictionary:/app/Dictionary \
        -v $(pwd)/requirements.txt:/app/requirements.txt \
        kaboom-server:1.1
}

start_interactive() {
    sudo docker run -it --rm --name $CONTAINER_NAME --network host $ENV_FILE \
        -v $(pwd)/Server:/app/Server \
        -v $(pwd)/Dictionary:/app/Dictionary \
        -v $(pwd)/requirements.txt:/app/requirements.txt \
        kaboom-server:1.1
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