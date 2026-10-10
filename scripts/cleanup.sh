#!/bin/bash
echo "Cleaning up mininet..."
sudo mn -c
echo "Killing lingering processes..."
sudo killall -9 ryu-manager iperf3 ping 2>/dev/null
if [ -f ../results/ryu.pid ]; then
    kill -9 $(cat ../results/ryu.pid) 2>/dev/null
    rm ../results/ryu.pid
fi
echo "Cleanup done."
