#!/bin/bash
cd "$(dirname "$0")"
echo "Cleaning up any old processes..."
./cleanup.sh

echo "Starting Ryu controller..."
./start_controller.sh

echo "Waiting for controller to boot (5 seconds)..."
sleep 5

echo "Running Mininet failover experiment..."
sudo python3 ../experiments/run_failover.py

echo "Generating plots and analysis..."
python3 ../analysis/plot_results.py

echo "Cleaning up..."
./cleanup.sh

echo "Experiment pipeline finished successfully!"
