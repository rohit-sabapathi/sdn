# Dynamic Routing Policy Using an SDN Controller

## Objective
Design and implement a dynamic routing policy using an SDN controller (Ryu) and Mininet. The project demonstrates normal forwarding, automatic rerouting after a link failure, and recovery verification, followed by performance analysis.

## Architecture and Topology
The custom Mininet topology consists of:
- **Hosts**: h1 and h2
- **Switches**: s1, s2, s3, and s4
- **Primary Path**: h1 -> s1 -> s2 -> s4 -> h2
- **Alternate Path**: h1 -> s1 -> s3 -> s4 -> h2

See `diagrams/topology.mmd` for the visual Mermaid diagram.

## Software Prerequisites
- Operating System: Ubuntu Linux (20.04 or 22.04 recommended).
- Mininet
- Open vSwitch (OVS)
- Python 3 with `pip`
- Ryu SDN Framework (OpenFlow 1.3)
- iperf3

## Installation Instructions (Ubuntu)
Run the setup script which installs system packages and Python requirements:
```bash
cd scripts/
chmod +x setup_ubuntu.sh
./setup_ubuntu.sh
```

## Running the Automated Experiment
We provide a unified script that starts the controller, runs the Mininet topology, conducts connectivity and throughput tests, simulates link failures, recovers the link, and generates graphs.

**To run the entire pipeline:**
```bash
cd scripts/
chmod +x *.sh
./run_experiment.sh
```

### Manual Steps Breakdown:
If you prefer to run the components manually, follow these steps:
1. **Start the Controller**:
   ```bash
   ryu-manager controller/dynamic_routing.py --verbose
   ```
2. **Start the Failover Test**:
   In a new terminal:
   ```bash
   sudo python3 experiments/run_failover.py
   ```
3. **Generate Plots and Analysis**:
   ```bash
   python3 analysis/plot_results.py
   python3 analysis/analyze_results.py
   ```
4. **Cleanup**:
   ```bash
   sudo ./scripts/cleanup.sh
   ```

## Troubleshooting
- **Ryu Import Errors**: Ensure you have `eventlet==0.30.2` if you encounter Python 3.10+ issues with Ryu.
- **Mininet Not Starting**: Run `sudo mn -c` to clear lingering network namespaces.
- **Port Status Not Firing**: Ensure the switches are configured to support OpenFlow 1.3 (`protocols='OpenFlow13'`).
