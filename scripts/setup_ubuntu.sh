#!/bin/bash
set -e

echo "Updating package list..."
sudo apt-get update

echo "Installing Mininet, Open vSwitch, and tools..."
sudo apt-get install -y mininet openvswitch-switch openvswitch-common python3-pip python3-tk iproute2 iputils-ping iperf3

echo "Installing Python requirements..."
pip3 install -r ../requirements.txt

echo "Setup completed successfully."
