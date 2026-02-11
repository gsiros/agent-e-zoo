#!/bin/bash
set -e

docker stop muzzle-agent-e 2>/dev/null || true
docker rm muzzle-agent-e 2>/dev/null || true
docker rmi muzzle-agent-e 2>/dev/null || true

xhost -local:docker 2>/dev/null || true

echo "Cleaned up."
