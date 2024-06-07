# P4-Mininet Examples

Follow [these](https://mininet.org/download/) instructions to install Mininet on your machine.

Follow [these](https://github.com/p4lang/p4c?tab=readme-ov-file#installing-p4c-from-source) instruction to install the P4C on your machine.

Follow [these](https://github.com/p4lang/behavioral-model?tab=readme-ov-file#installing-bmv2) instructions to install BMv2 software switch.

You can use the following invocation to show the supported target,arch pairs

    p4c --target-help

    Supported targets in "target, arch" tuple:
    dpdk-psa
    bmv2-v1model
    bmv2-psa
    ebpf-v1model

Compile the P4 program by:

    p4c --target bmv2 --arch v1model --std p4-16 simple_forward.p4

Invoke `run_mininet.py` Python script and pass the BMv2 JSON file to it:

    sudo run_mininet.py --switch_json simple_forward.json

It starts a Mininet instance with three simple_switch (s1, s2, s3) configured in a triangle, each connected to one host (h1, h2, h3). The hosts are assigned IPs of 10.0.1.1, 10.0.2.2, and 10.0.3.3.

Open two terminals for h1 and h2, respectively:

    mininet> xterm h1 h2

We are going to use scapy to send traffic between the hosts.

Run the `receive.py` Python script on h2:

    mininet> ./receive.py

And run the `send.py` Python script on h1:

    mininet> ./send.py 10.0.2.2 "P4 is cool"

You should be able to see the message on host h2.

You can use the following command to interact with a running BMv2 software switch instance using its CLI.

    simple_switch_CLI --thrift-port 9090
