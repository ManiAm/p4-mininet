#!/bin/bash

# Start Open vSwitch
echo "[INFO] Starting Open vSwitch..."
service openvswitch-switch start

# Start an interactive shell or run passed commands
exec "$@"
