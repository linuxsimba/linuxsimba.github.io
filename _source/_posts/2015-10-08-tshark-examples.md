---
title: Tshark Command Examples
tags: ['wireshark', 'sniffer']
---

> Updated 27th Feb 2016

This is a collection of Tshark command examples

I find using Tshark more convenient than TCPDump. Great tool to have when
troubleshooting Openstack hypervisors and Cumulus Linux switches.

To capture packets as a non-root user, use the _[running wireshark as
you](https://blog.wireshark.org/2010/02/running-wireshark-as-you/)_
posting.


### Define a Capture filter, output data to a file, print summary

In this example, I capture only DHCP packets during a switch bootup and
installation of software.


[_(Explain Shell Command_)](http://explainshell.com/explain?cmd=tshark+-w+%2Ftmp%2Fdhcp.pcap+-f+%22port+67+or+port+68%22+-i+eth1+-P)

```
$ sudo tshark -w /tmp/dhcp.pcap -f "port 67 or port 68" -i eth1 -P

 [string "/usr/share/wireshark/init.lua"]:46: dofile has been disabled due to
running Wireshark as superuser. See
http://wiki.wireshark.org/CaptureSetup/CapturePrivileges for help in running
Wireshark as an unprivileged user.
Running as user "root" and group "root". This could be dangerous.
Capturing on 'eth1'
  1   0.000000      0.0.0.0 -> 255.255.255.255 DHCP 412 DHCP Discover - Transaction ID 0xe67e92f
  2   0.000303  192.168.0.1 -> 192.168.0.11 DHCP 352 DHCP Offer    - Transaction ID 0xe67e92f
  3   0.007959      0.0.0.0 -> 255.255.255.255 DHCP 424 DHCP Request  - Transaction ID 0xe67e92f
  4   0.008161  192.168.0.1 -> 192.168.0.11 DHCP 352 DHCP ACK      - Transaction ID 0xe67e92f
  5   1.221991      0.0.0.0 -> 255.255.255.255 DHCP 412 DHCP Discover - Transaction ID 0x2a0d7db9
  6   1.222243  192.168.0.1 -> 192.168.0.11 DHCP 352 DHCP Offer    - TransactionID 0x2a0d7db9
  7   1.229958      0.0.0.0 -> 255.255.255.255 DHCP 424 DHCP Request  - Transaction ID 0x2a0d7db9

```


### View the content of a wireshark file, list summary

```
$ tshark -r /tmp/dhcp.pcap
  1 0.000000000      0.0.0.0 -> 255.255.255.255 DHCP 412 DHCP Discover - Transaction ID 0xe67e92f
  2 0.000303000  192.168.0.1 -> 192.168.0.11 DHCP 352 DHCP Offer    - Transaction ID 0xe67e92f
  3 0.007959000      0.0.0.0 -> 255.255.255.255 DHCP 424 DHCP Request  - Transaction ID 0xe67e92f
  ...
  .....
```

### Apply a display filter on the captured data

In this example, I show how to only view DHCP discover packets from a trace with
all DHCP packets. Got this info from the [bootp Wireshark display
reference](https://www.wireshark.org/docs/dfref/b/bootp.html)

```
$ tshark -r ~/dhcp.pcap bootp.option.dhcp == 1
  1 0.000000000      0.0.0.0 -> 255.255.255.255 DHCP 412 DHCP Discover - Transaction ID 0xe67e92f
  5 1.221991000      0.0.0.0 -> 255.255.255.255 DHCP 412 DHCP Discover - Transaction ID 0x2a0d7db9
 10 2.563975000      0.0.0.0 -> 255.255.255.255 DHCP 418 DHCP Discover - Transaction ID 0x561a89f0
 23 369.485935000      0.0.0.0 -> 255.255.255.255 DHCP 342 DHCP Discover - Transaction ID 0x6060d04c

```

### View the contents of a single packet.

Tshark prints out data exactly like wireshark. After I found this out, I have
stopped using tcpdump!


```
$ tshark -r ~/dhcp.pcap -V frame.number == 1
Frame 1: 412 bytes on wire (3296 bits), 412 bytes captured (3296 bits) on
interface 0
    Interface id: 0
    Encapsulation type: Ethernet (1)
    Arrival Time: Oct  8, 2015 13:13:54.793473000 UTC
    [Time shift for this packet: 0.000000000 seconds]
    Epoch Time: 1444310034.793473000 seconds
    [Time delta from previous captured frame: 0.000000000 seconds]
    [Time delta from previous displayed frame: 0.000000000 seconds]
    [Time since reference or first frame: 0.000000000 seconds]
    Frame Number: 1
    Frame Length: 412 bytes (3296 bits)
    Capture Length: 412 bytes (3296 bits)
    [Frame is marked: False]
    [Frame is ignored: False]
    [Protocols in frame: eth:ip:udp:bootp]
Ethernet II, Src: Edgecore_be:0c:ef (70:72:cf:be:0c:ef), Dst: Broadcast
(ff:ff:ff:ff:ff:ff)
    Destination: Broadcast (ff:ff:ff:ff:ff:ff)
        Address: Broadcast (ff:ff:ff:ff:ff:ff)
        .... ..1. .... .... .... .... = LG bit: Locally administered address
(this is NOT the factory default)
        .... ...1 .... .... .... .... = IG bit: Group address
(multicast/broadcast)
    Source: Edgecore_be:0c:ef (70:72:cf:be:0c:ef)
        Address: Edgecore_be:0c:ef (70:72:cf:be:0c:ef)
        .... ..0. .... .... .... .... = LG bit: Globally unique address (factory
default)
        .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
    Type: IP (0x0800)
Internet Protocol Version 4, Src: 0.0.0.0 (0.0.0.0), Dst: 255.255.255.255
(255.255.255.255)
    Version: 4
    Header length: 20 bytes
    Differentiated Services Field: 0x00 (DSCP 0x00: Default; ECN: 0x00: Not-ECT
(Not ECN-Capable Transport))
        0000 00.. = Differentiated Services Codepoint: Default (0x00)
        .... ..00 = Explicit Congestion Notification: Not-ECT (Not ECN-Capable
Transport) (0x00)
    Total Length: 398
    Identification: 0x0000 (0)
    Flags: 0x00
        0... .... = Reserved bit: Not set
        .0.. .... = Don't fragment: Not set
        ..0. .... = More fragments: Not set
    Fragment offset: 0
    Time to live: 64
    Protocol: UDP (17)
    Header checksum: 0x7960 [validation disabled]
        [Good: False]
        [Bad: False]
    Source: 0.0.0.0 (0.0.0.0)
    Destination: 255.255.255.255 (255.255.255.255)
    [Source GeoIP: Unknown]
    [Destination GeoIP: Unknown]
User Datagram Protocol, Src Port: bootpc (68), Dst Port: bootps (67)
    Source port: bootpc (68)
    Destination port: bootps (67)
    Length: 378
    Checksum: 0xe9be [validation disabled]
        [Good Checksum: False]
        [Bad Checksum: False]
Bootstrap Protocol
    Message type: Boot Request (1)
    Hardware type: Ethernet (0x01)
    Hardware address length: 6
    Hops: 0
    Transaction ID: 0x0e67e92f
    Seconds elapsed: 0
    Bootp flags: 0x0000 (Unicast)
        0... .... .... .... = Broadcast flag: Unicast
        .000 0000 0000 0000 = Reserved flags: 0x0000
    Client IP address: 0.0.0.0 (0.0.0.0)
    Your (client) IP address: 0.0.0.0 (0.0.0.0)
    Next server IP address: 0.0.0.0 (0.0.0.0)
    Relay agent IP address: 0.0.0.0 (0.0.0.0)
    Client MAC address: Edgecore_be:0c:ef (70:72:cf:be:0c:ef)
    Client hardware address padding: 00000000000000000000
    Server host name not given
    Boot file name not given
   ...
   ......
   ...........
```

### Reviewing VxLAN Data

The following examples are from an Openstack Hypervisor that has
[VTEPs](http://www.netcraftsmen.com/vxlan-virtual-extensible-lan/)

The Openstack hypervisor uses UDP port 8472 instead of port 4789 for all VxLAN
traffic.

The first example shows how to execute the [Wireshark Decode As Protocol
function](https://www.wireshark.org/docs/wsug_html_chunked/ChCustProtocolDissectionSection.html#ChAdvDecodeAsFig) in tshark. All UDP packets using port 8472 are going to be decoded
as VxLAN packets and the content inside the VxLAN can be then be filtered. The
example shows how to look for duplicate ACKs in a VxLAN encapsulated TCP
stream.


[_(Explain Shell
Command)_](http://explainshell.com/explain?cmd=tshark++-d+udp.port%3D%3D8472%2Cvxlan+-r+1.cap+%22tcp.analysis.duplicate_ack_num%3D%3D1%22)

```
$ tshark  -d udp.port==8472,vxlan -r 1.cap "tcp.analysis.duplicate_ack_num==1"

223 0.016157000 10.100.1.100 -> 10.100.1.102 TCP 128 [TCP Dup ACK 222#1] commplex-link > 44736 [ACK] Seq=1 Ack=5888377 Win=23504 Len=0 TSval=50575 TSecr=2178171 SLE=5889775 SRE=5892571
444 0.027179000 10.100.1.100 -> 10.100.1.102 TCP 128 [TCP Dup ACK 442#1] commplex-link > 44736 [ACK] Seq=1 Ack=9091195 Win=24408 Len=0 TSval=50577 TSecr=2178174 SLE=9190453 SRE=9193249
```

The packets without decoding look like this:

```
$tshark  -r 1.cap "frame.number==223||frame.number==444"

223 0.016157000 192.168.40.5 -> 192.168.40.2 UDP 128 Source port: 55732 Destination port: otv
444 0.027179000 192.168.40.5 -> 192.168.40.2 UDP 128 Source port: 55732 Destination port: otv

```

Tshark does provide full header information of the inner and outer IP headers of
the VxLAN packet. It is hard not to love Tshark!

```
tshark  -d udp.port==8472,vxlan -r 1.cap "frame.number==223"  -V
Frame 223: 128 bytes on wire (1024 bits), 128 bytes captured (1024 bits) on
interface 0
    Interface id: 0
    Encapsulation type: Ethernet (1)
    Arrival Time: Feb 27, 2016 14:48:33.401614000 EST
    [Time shift for this packet: 0.000000000 seconds]
    Epoch Time: 1456602513.401614000 seconds
    [Time delta from previous captured frame: 0.000020000 seconds]
    [Time delta from previous displayed frame: 0.000000000 seconds]
    [Time since reference or first frame: 0.016157000 seconds]
    Frame Number: 223
    Frame Length: 128 bytes (1024 bits)
    Capture Length: 128 bytes (1024 bits)
    [Frame is marked: False]
    [Frame is ignored: False]
    [Protocols in frame: eth:ip:udp:vxlan:eth:ip:tcp]
Ethernet II, Src: 3c:fd:fe:9c:b6:d1 (3c:fd:fe:9c:b6:d1), Dst: Edgecore_be:12:f7
(70:72:cf:be:12:f7)
    Destination: Edgecore_be:12:f7 (70:72:cf:be:12:f7)
        Address: Edgecore_be:12:f7 (70:72:cf:be:12:f7)
        .... ..0. .... .... .... .... = LG bit: Globally unique address (factory
default)
        .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
    Source: 3c:fd:fe:9c:b6:d1 (3c:fd:fe:9c:b6:d1)
        Address: 3c:fd:fe:9c:b6:d1 (3c:fd:fe:9c:b6:d1)
        .... ..0. .... .... .... .... = LG bit: Globally unique address (factory
default)
        .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
    Type: IP (0x0800)
Internet Protocol Version 4, Src: 192.168.40.5 (192.168.40.5), Dst: 192.168.40.2
(192.168.40.2)
    Version: 4
    Header length: 20 bytes
    Differentiated Services Field: 0x00 (DSCP 0x00: Default; ECN: 0x00: Not-ECT
(Not ECN-Capable Transport))
        0000 00.. = Differentiated Services Codepoint: Default (0x00)
        .... ..00 = Explicit Congestion Notification: Not-ECT (Not ECN-Capable
Transport) (0x00)
    Total Length: 114
    Identification: 0xf6f3 (63219)
    Flags: 0x00
        0... .... = Reserved bit: Not set
        .0.. .... = Don't fragment: Not set
        ..0. .... = More fragments: Not set
    Fragment offset: 0
    Time to live: 10
    Protocol: UDP (17)
    Header checksum: 0xe82f [validation disabled]
        [Good: False]
        [Bad: False]
    Source: 192.168.40.5 (192.168.40.5)
    Destination: 192.168.40.2 (192.168.40.2)
    [Source GeoIP: Unknown]
    [Destination GeoIP: Unknown]
User Datagram Protocol, Src Port: 55732 (55732), Dst Port: otv (8472)
    Source port: 55732 (55732)
    Destination port: otv (8472)
    Length: 94
    Checksum: 0x0000 (none)
        [Good Checksum: False]
        [Bad Checksum: False]
Virtual eXtensible Local Area Network
    Flags: 0x08
        0... .... = Reserved(R): False
        .0.. .... = Reserved(R): False
        ..0. .... = Reserved(R): False
        ...0 .... = Reserved(R): False
        .... 1... = VXLAN Network ID(VNI): Present
        ...0 .... = Reserved(R): False
        ...0 .... = Reserved(R): False
        ...0 .... = Reserved(R): False
    Reserved: 0x000000
    VXLAN Network Identifier (VNI): 2008
    Reserved: 0
Ethernet II, Src: fa:16:3e:eb:d1:8e (fa:16:3e:eb:d1:8e), Dst: fa:16:3e:b1:d5:bd
(fa:16:3e:b1:d5:bd)
    Destination: fa:16:3e:b1:d5:bd (fa:16:3e:b1:d5:bd)
        Address: fa:16:3e:b1:d5:bd (fa:16:3e:b1:d5:bd)
        .... ..1. .... .... .... .... = LG bit: Locally administered address
(this is NOT the factory default)
        .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
    Source: fa:16:3e:eb:d1:8e (fa:16:3e:eb:d1:8e)
        Address: fa:16:3e:eb:d1:8e (fa:16:3e:eb:d1:8e)
        .... ..1. .... .... .... .... = LG bit: Locally administered address
(this is NOT the factory default)
        .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
    Type: IP (0x0800)
Internet Protocol Version 4, Src: 10.100.1.100 (10.100.1.100), Dst: 10.100.1.102
(10.100.1.102)
    Version: 4
    Header length: 20 bytes
    Differentiated Services Field: 0x00 (DSCP 0x00: Default; ECN: 0x00: Not-ECT
(Not ECN-Capable Transport))
        0000 00.. = Differentiated Services Codepoint: Default (0x00)
        .... ..00 = Explicit Congestion Notification: Not-ECT (Not ECN-Capable
Transport) (0x00)
    Total Length: 64
    Identification: 0xa03f (41023)
    Flags: 0x02 (Don't Fragment)
        0... .... = Reserved bit: Not set
        .1.. .... = Don't fragment: Set
        ..0. .... = More fragments: Not set
    Fragment offset: 0
    Time to live: 64
    Protocol: TCP (6)
    Header checksum: 0x82e7 [validation disabled]
        [Good: False]
        [Bad: False]
    Source: 10.100.1.100 (10.100.1.100)
    Destination: 10.100.1.102 (10.100.1.102)
    [Source GeoIP: Unknown]
    [Destination GeoIP: Unknown]
Transmission Control Protocol, Src Port: commplex-link (5001), Dst Port: 44736
(44736), Seq: 1, Ack: 5888377, Len: 0
    Source port: commplex-link (5001)
    Destination port: 44736 (44736)
    [Stream index: 0]
    Sequence number: 1    (relative sequence number)
    Acknowledgment number: 5888377    (relative ack number)
    Header length: 44 bytes
    Flags: 0x010 (ACK)
        000. .... .... = Reserved: Not set
        ...0 .... .... = Nonce: Not set
        .... 0... .... = Congestion Window Reduced (CWR): Not set
        .... .0.. .... = ECN-Echo: Not set
        .... ..0. .... = Urgent: Not set
        .... ...1 .... = Acknowledgment: Set
        .... .... 0... = Push: Not set
        .... .... .0.. = Reset: Not set
        .... .... ..0. = Syn: Not set
        .... .... ...0 = Fin: Not set
    Window size value: 23504
    [Calculated window size: 23504]
    [Window size scaling factor: -1 (unknown)]
    Checksum: 0x17c4 [validation disabled]
        [Good Checksum: False]
        [Bad Checksum: False]
    Options: (24 bytes), No-Operation (NOP), No-Operation (NOP), Timestamps,
No-Operation (NOP), No-Operation (NOP), SACK
        No-Operation (NOP)
            Type: 1
                0... .... = Copy on fragmentation: No
                .00. .... = Class: Control (0)
                ...0 0001 = Number: No-Operation (NOP) (1)
        No-Operation (NOP)
            Type: 1
                0... .... = Copy on fragmentation: No
                .00. .... = Class: Control (0)
                ...0 0001 = Number: No-Operation (NOP) (1)
        Timestamps: TSval 50575, TSecr 2178171
            Kind: Timestamp (8)
            Length: 10
            Timestamp value: 50575
            Timestamp echo reply: 2178171
        No-Operation (NOP)
            Type: 1
                0... .... = Copy on fragmentation: No
                .00. .... = Class: Control (0)
                ...0 0001 = Number: No-Operation (NOP) (1)
        No-Operation (NOP)
            Type: 1
                0... .... = Copy on fragmentation: No
                .00. .... = Class: Control (0)
                ...0 0001 = Number: No-Operation (NOP) (1)
        SACK: 5889775-5892571
            left edge = 5889775 (relative)
            right edge = 5892571 (relative)
            [TCP SACK Count: 1]
    [SEQ/ACK analysis]
        [TCP Analysis Flags]
            [This is a TCP duplicate ack]
        [Duplicate ACK #: 1]
        [Duplicate to the ACK in frame: 222]
            [Expert Info (Note/Sequence): Duplicate ACK (#1)]
                [Message: Duplicate ACK (#1)]
                [Severity level: Note]
                [Group: Sequence]
```
