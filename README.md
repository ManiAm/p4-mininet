# P4-Mininet

The p4-mininet project is a lightweight, containerized P4 network simulation environment built using Docker, Mininet, and BMv2, enabling users to experiment with basic IPv4 forwarding through a custom P4 program. The setup includes a pre-configured Docker container running Mininet and Open vSwitch on the host, and it leverages the BMv2 software switch to emulate programmable data planes.

The following guides provide an introduction to Mininet and P4:

- [Mininet Introduction](mininet.md)
- [P4 Introduction](p4.md)

## Getting Started

Install Open vSwitch on the host machine:

```bash
sudo apt install openvswitch-switch
sudo modprobe openvswitch
sudo systemctl start openvswitch-switch
```

And verify it:

```bash
sudo ovs-vsctl show

e1e8d137-d2ac-4b32-8403-c5d82a33f105
    ovs_version: "3.3.0"
```

Build the mininet-img:

```bash
docker build --tag mininet-img .
```

Start the container:

```bash
docker compose up -d
```

Open an interactive shell to the mininet container:

```bash
docker exec -it mininet bash
```

And verify that it is working:

```bash
sudo mn --test pingall
```

## Basic Forwarding Using P2

The [simple_forward.p4](simple_forward/p4_program/simple_forward.p4) program is designed to perform basic IPv4 forwarding based on the destination IP address. It consists of six control blocks: `parser`, `verify_checksum`, `ingress`, `egress`, `compute_checksum` and `deparser`. The V1Switch block connects these blocks to form the complete packet processing pipeline.

The **parser** block (my_parser) is responsible for extracting headers from incoming packets and filling the header structures with the extracted data. It starts by extracting the Ethernet header in the initial state (start). If the EtherType indicates that the packet is an IPv4 packet (0x0800), the parser transitions to the parse_ipv4 state. In this state, it extracts the IPv4 header and verifies that the version is set to 4 (indicating an IPv4 packet) and that the Internet Header Length (IHL) is set to 5 (indicating no IP options). If these conditions are met, the parser transitions to the accept state, indicating successful parsing.

The **ingress** control block (my_ingress) handles the main packet processing and decision-making logic within the switch. It defines two actions: drop, which marks the packet to be dropped, and ipv4_forward, which updates the Ethernet source and destination addresses, decrements the IPv4 TTL, and sets the egress port. The ipv4_lpm table performs a longest prefix match (LPM) on the destination IPv4 address and invokes either the ipv4_forward or drop action based on the match. The apply block in MyIngress checks if the IPv4 header is valid and applies the ipv4_lpm table.

The **egress** control block (my_egress) is designed for processing packets after they have passed through the ingress control and before they are transmitted out of the switch. Although this block is currently empty, it serves as a placeholder for any processing that might be necessary at the egress stage, such as additional header modifications or egress-specific actions.

The **deparser** block (my_deparser) reassembles the packet for transmission after it has been processed. It emits the Ethernet header followed by the IPv4 header back into the packet, ensuring that the packet is correctly formatted for transmission out of the switch.

## Using BMV2 Target

Compile the P4 program by:

```bash
cd /opt/simple_forward/p4_program/
p4c --target bmv2 --arch v1model --std p4-16 simple_forward.p4
```

This command specifies the target as BMv2 and the architecture as v1model, which is a common model used for the BMv2 software switch. The compiler generates a JSON file named `simple_forward.json` that describes the packet processing pipeline and can be loaded onto the BMv2 switch. BMv2 is a software switch that acts as a reference implementation for the P4 language. It serves as a virtual platform for testing and validating P4 programs. 

Invoke `run_mininet.py` Python script and pass the BMv2 JSON file to it:

```bash
cd /opt/simple_forward
sudo /usr/bin/python3 run_mininet.py --switch_json ./p4_program/simple_forward.json
```

It starts a Mininet instance with three simple_switch (s1, s2, s3) configured in a triangle, each connected to one host (h1, h2, h3). The hosts are assigned IPs of 10.0.1.1, 10.0.2.2, and 10.0.3.3. Each BMv2 switch in started with an invocation like the following.

```bash
simple_switch --log-console -i 1@s1-eth1 -i 2@s1-eth2 -i 3@s1-eth3 --pcap --thrift-port 9090 --nanolog ipc:///tmp/bm-0-log.ipc --device-id 0 simple_forward.json 
```

Note that the `-i` option is used to specify the mapping between switch ports and network interfaces. This mapping is crucial for the BMv2 switch to know which physical or virtual network interfaces correspond to its logical ports. Here, logical port 1 of the switch is mapped to the host's network interface eth1, and logical port 2 of the switch is mapped to the host's network interface eth2, and so on.

The `Thrift` server allows external programs to communicate with the switch, typically for control and configuration purposes. In this case, it is set to listen on port 9090. We are also configuring `nanolog`, a lightweight logging mechanism. Logs will be written to the specified IPC path (`ipc:///tmp/bm-0-log.ipc`). Finally, we are setting device ID to 0. It is useful when running multiple instances of the switch on the same host, as it uniquely identifies each instance.

Open two terminals for h1 and h2, respectively:

```bash
mininet> xterm h1 h2
```

Run the `receive.py` Python script on h2. We use scapy to sniff on port h2-eth0, and print any TCP packet with destination port 1234.

```bash
mininet> ./receive.py
```

Run the `send.py` Python script on h1. The message from the command-line is encapsulated into a TCP packet with destination port 1234. The TCP packet then gets encapsulated in an IP packet with destination IP address of h2 (10.0.2.2) and is sent out in a broadcast Ethernet frame.

```bash
mininet> ./send.py 10.0.2.2 "P4 is cool"
```

You should be able to see the message on host h2. 

## Control Plane

Our P4 program defines a packet-processing pipeline, but the rules within each table are inserted by the control plane. When a rule matches a packet, its action is invoked with parameters supplied by the control plane as part of the rule. 

As part of bringing up the Mininet instance, `run_mininet.py` Python script installs packet-processing rules in the tables of each switch. These rules are defined in the `sX-commands.txt` files, where `X` corresponds to the switch number. Here are sample rules for s1:

```text
table_set_default ipv4_lpm drop
table_add ipv4_lpm ipv4_forward 10.0.1.1/32 => 00:00:00:00:01:01 1
table_add ipv4_lpm ipv4_forward 10.0.2.2/32 => 00:00:00:02:02:00 2
table_add ipv4_lpm ipv4_forward 10.0.3.3/32 => 00:00:00:03:03:00 3
```

These commands are written in the **P4Runtime** API language. P4Runtime is an API used to control and manage P4-programmed devices at runtime. It allows for operations such as setting default actions for tables (`table_set_default`), and adding entries to tables (`table_add`), specifying how packets should be forwarded based on match criteria (e.g., IP addresses).

Use the following command to interact with a running BMv2 software switch instance using its CLI to query or modify the switch's state.

```bash
simple_switch_CLI --thrift-port 9090

Obtaining JSON from switch...
Done
Control utility for runtime P4 table manipulation
RuntimeCmd:
```

The `show_tables` command reports that there is a `my_ingress.ipv4_lpm` table:

```bash
RuntimeCmd: show_tables
my_ingress.ipv4_lpm      [implementation=None, mk=ipv4.dstAddr(lpm, 32)]
```

The `table_dump` command shows the entries on the table.

```bash
RuntimeCmd: table_dump ipv4_lpm

==========
TABLE ENTRIES
**********
Dumping entry 0x0
Match key:
* ipv4.dstAddr        : LPM       0a000101/32
Action entry: my_ingress.ipv4_forward - 0101, 01
**********
Dumping entry 0x1
Match key:
* ipv4.dstAddr        : LPM       0a000202/32
Action entry: my_ingress.ipv4_forward - 020200, 02
**********
Dumping entry 0x2
Match key:
* ipv4.dstAddr        : LPM       0a000303/32
Action entry: my_ingress.ipv4_forward - 030300, 03
==========
Dumping default entry
Action entry: my_ingress.drop - 
==========
```

## Note

You can find more P4 tutorials in [here](https://github.com/p4lang/tutorials).
