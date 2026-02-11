#!/bin/bash
set -e

docker stop agent-e 2>/dev/null || true
docker rm agent-e 2>/dev/null || true
docker rmi agent-e 2>/dev/null || true

xhost -local:docker 2>/dev/null || true

echo "Cleaned up."
