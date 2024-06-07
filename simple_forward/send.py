#!/usr/bin/env python3

import sys
import socket
import random

from scapy.all import sendp, get_if_list, get_if_hwaddr
from scapy.all import Ether, IP, TCP

def get_if():

    iface = None # "h1-eth0"

    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break

    if not iface:
        print("Cannot find eth0 interface")
        exit(1)

    return iface


def main():

    if len(sys.argv) < 3:
        print('pass 2 arguments: <destination> "<message>"')
        exit(1)

    iface = get_if()
    addr = socket.gethostbyname(sys.argv[1])
    print(f"sending on interface {iface} to {addr}")

    # create the packet
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt /IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / sys.argv[2]
    pkt.show2()

    # and send it
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':

    main()
