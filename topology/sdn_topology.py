from mininet.topo import Topo
from mininet.link import TCLink

class DualPathTopo(Topo):
    def build(self, **_opts):
        # Add hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')

        # Add switches
        s1 = self.addSwitch('s1', protocols='OpenFlow13')
        s2 = self.addSwitch('s2', protocols='OpenFlow13')
        s3 = self.addSwitch('s3', protocols='OpenFlow13')
        s4 = self.addSwitch('s4', protocols='OpenFlow13')

        # Add links with specific ports to make them predictable
        # Host links
        self.addLink(h1, s1, port1=1, port2=1, cls=TCLink, bw=100, delay='1ms')
        self.addLink(s4, h2, port1=3, port2=1, cls=TCLink, bw=100, delay='1ms')
        
        # Primary path links
        self.addLink(s1, s2, port1=2, port2=1, cls=TCLink, bw=10, delay='5ms')
        self.addLink(s2, s4, port1=2, port2=1, cls=TCLink, bw=10, delay='5ms')
        
        # Alternate path links
        self.addLink(s1, s3, port1=3, port2=1, cls=TCLink, bw=10, delay='10ms')
        self.addLink(s3, s4, port1=2, port2=2, cls=TCLink, bw=10, delay='10ms')

# This dictionary is useful for mininet '--topo' command line argument
topos = { 'dualpath': ( lambda: DualPathTopo() ) }
