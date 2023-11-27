#!/bin/bash
set -o allexport
source .env
set +o allexport

if [[ $1 == 's' ]]; then
    uvicorn server.main:app --reload --host 0.0.0.0 --port 9090
elif [[ $1 == 'l' ]]; then
    pylsp --ws --port 9095
else
    echo "Invalid argument, please use 's' for server and 'l' for lsp."
fi