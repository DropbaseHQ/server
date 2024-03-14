#!/bin/bash

if [[ $1 == 's' ]]; then
    docker image rm dropbase/worker
    docker network create dropbase_default
    docker build -t dropbase/worker -f Dockerfile-worker .
    pip install -U -e dropbase/.
    uvicorn server.main:app --reload --reload-dir server/ --host 0.0.0.0 --port 9090
elif [[ $1 == 'l' ]]; then
    pylsp --ws --port 9095
else
    echo "Invalid argument, please use 's' for server and 'l' for lsp."
fi