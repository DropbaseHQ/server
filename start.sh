#!/bin/sh

# Install additional packages
if [ -f /project/requirements/requirements.txt ]; then
    pip install -r /project/requirements/requirements.txt
fi


# Start the server
cd /project
uvicorn server.main:app --reload --host 0.0.0.0 --port 9090