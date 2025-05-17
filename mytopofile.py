from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel

class MyTopo(Topo):

    def build(self):
        # Add hosts and switches
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(s1, s2)

topos = {'mytopo': (lambda: MyTopo())}

if __name__ == '__main__':

    setLogLevel('info')
    topo = MyTopo()
    net = Mininet(topo=topo, controller=Controller)
    net.start()
    CLI(net)  # Run the CLI for interactive commands
    net.stop()
