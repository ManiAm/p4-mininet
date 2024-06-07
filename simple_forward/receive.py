#!/usr/bin/env python3

import sys

from scapy.all import sniff, get_if_list
from scapy.all import IPOption
from scapy.all import ShortField, IntField, FieldListField, FieldLenField
from scapy.all import TCP
from scapy.layers.inet import _IPOption_HDR

def get_if():

    iface = None

    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break

    if not iface:
        print("Cannot find eth0 interface")
        exit(1)

    return iface


class IPOption_MRI(IPOption):

    name = "MRI"
    option = 31

    fields_desc = [ _IPOption_HDR,
                    FieldLenField("length", None, fmt="B",
                                  length_of="swids",
                                  adjust=lambda pkt,l:l+4),
                    ShortField("count", 0),
                    FieldListField("swids",
                                   [],
                                   IntField("", 0),
                                   length_from=lambda pkt:pkt.count*4) ]

def handle_pkt(pkt):

    if TCP in pkt and pkt[TCP].dport == 1234:
        print("got a packet")
        pkt.show2()
        sys.stdout.flush()


def main():

    iface = get_if()
    print(f"sniffing on {iface}")
    sys.stdout.flush()

    sniff(iface = iface, prn = lambda x: handle_pkt(x))


if __name__ == '__main__':

    main()
