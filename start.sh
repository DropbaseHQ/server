#!/bin/sh

# Install additional packages
if [ -f /project/requirements-custom.txt ]; then
    pip install -r /project/requirements-custom.txt
fi


# Start the server
cd /project
uvicorn server.main:app --host 0.0.0.0 --port 9090