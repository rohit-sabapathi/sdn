#!/bin/bash
echo "Starting Ryu Controller in the background..."
# Note: run from the scripts directory or adjust path
ryu-manager ../controller/dynamic_routing.py --verbose > ../results/controller.log 2>&1 &
echo $! > ../results/ryu.pid
echo "Controller started."
