import sys
import os
import time
import json
import csv
import re
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.log import setLogLevel, info

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from topology.sdn_topology import DualPathTopo

def parse_ping(ping_output):
    loss = 100.0
    latency = 0.0
    loss_match = re.search(r'(\d+)% packet loss', ping_output)
    if loss_match:
        loss = float(loss_match.group(1))
    rtt_match = re.search(r'rtt min/avg/max/mdev = [\d\.]+/(.*?)/[\d\.]+/', ping_output)
    if rtt_match:
        latency = float(rtt_match.group(1))
    return loss, latency

def run_experiment():
    setLogLevel('info')
    
    info('*** Creating network\n')
    topo = DualPathTopo()
    net = Mininet(topo=topo, controller=RemoteController, switch=OVSSwitch)
    
    info('*** Adding controller\n')
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)
    
    info('*** Starting network\n')
    net.start()
    
    info('*** Waiting for controller to install flows (5s)...\n')
    time.sleep(5)
    
    h1, h2 = net.get('h1', 'h2')
    
    results = []

    def measure_throughput():
        h2.cmd('iperf3 -s -D')
        time.sleep(1)
        iperf_out = h1.cmd('iperf3 -c 10.0.0.2 -t 5 -J')
        h2.cmd('killall -9 iperf3')
        try:
            data = json.loads(iperf_out)
            return data['end']['sum_received']['bits_per_second'] / 1000000.0
        except Exception as e:
            info(f"Failed to parse iperf3: {e}\n")
            return 0.0

    # Scenario A: Normal Network
    info('\n=== Scenario A: Normal Network ===\n')
    ping_out = h1.cmd('ping -c 5 10.0.0.2')
    loss_a, lat_a = parse_ping(ping_out)
    throughput_a = measure_throughput()
    results.append({'Scenario': 'Normal', 'Loss(%)': loss_a, 'Latency(ms)': lat_a, 'Throughput(Mbps)': throughput_a})
    info(f"Normal -> Loss: {loss_a}%, Latency: {lat_a}ms, Throughput: {throughput_a:.2f} Mbps\n")

    # Scenario B: Failover
    info('\n=== Scenario B: Failover ===\n')
    info('Simulating link failure (s1-s2)...\n')
    fail_start = time.time()
    net.configLinkStatus('s1', 's2', 'down')
    
    recovered = False
    fail_end = 0
    for i in range(20):
        out = h1.cmd('ping -c 1 -W 1 10.0.0.2')
        if "1 received" in out or "0% packet loss" in out:
            fail_end = time.time()
            recovered = True
            break
        time.sleep(0.5)
        
    rerouting_time = (fail_end - fail_start) if recovered else -1
    info(f'Rerouting and recovery time: {rerouting_time:.2f} seconds\n')
    
    ping_out = h1.cmd('ping -c 5 10.0.0.2')
    loss_b, lat_b = parse_ping(ping_out)
    throughput_b = measure_throughput()
    results.append({'Scenario': 'Failover', 'Loss(%)': loss_b, 'Latency(ms)': lat_b, 'Throughput(Mbps)': throughput_b})
    info(f"Failover -> Loss: {loss_b}%, Latency: {lat_b}ms, Throughput: {throughput_b:.2f} Mbps\n")

    # Scenario C: Restoration
    info('\n=== Scenario C: Restoration ===\n')
    info('Restoring link (s1-s2)...\n')
    net.configLinkStatus('s1', 's2', 'up')
    time.sleep(3)
    
    ping_out = h1.cmd('ping -c 5 10.0.0.2')
    loss_c, lat_c = parse_ping(ping_out)
    throughput_c = measure_throughput()
    results.append({'Scenario': 'Restored', 'Loss(%)': loss_c, 'Latency(ms)': lat_c, 'Throughput(Mbps)': throughput_c})
    info(f"Restored -> Loss: {loss_c}%, Latency: {lat_c}ms, Throughput: {throughput_c:.2f} Mbps\n")

    info('\n*** Stopping network\n')
    net.stop()
    
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    csv_file = os.path.join(results_dir, 'metrics.csv')
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Scenario', 'Loss(%)', 'Latency(ms)', 'Throughput(Mbps)'])
        writer.writeheader()
        writer.writerows(results)
    info(f'Metrics saved to {csv_file}\n')

if __name__ == '__main__':
    run_experiment()
