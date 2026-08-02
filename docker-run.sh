#!/bin/bash
set -e

xhost +local:docker 2>/dev/null || true

docker run --rm -it \
    -e DISPLAY="$DISPLAY" \
    -e AUTOGEN_MODEL_API_KEY="$OPENAI_API_KEY" \
    -e AUTOGEN_MODEL_NAME="gpt-4o" \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    --env-file .env \
    --network host \
    --name muzzle-agent-e \
    muzzle-agent-e
