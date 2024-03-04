#!/bin/bash
docker run \
    --rm \
    --privileged \
    -p 2003:2003/tcp \
    -p 10001:10001/tcp \
    --env advertise=false \
    --env debug_mode=true \
    --env debug_port=10001 \
    --mount type=bind,source="$(pwd)"/meross_local_broker/rootfs/opt/custom_broker,target=/opt/custom_broker \
    -v "$(pwd)/.local_debug/data":/data local/meross_local_broker
