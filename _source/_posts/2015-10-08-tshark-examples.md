---
title: Tshark Command Examples
tags: ['wireshark', 'sniffer']
---

Just a collection of Tshark commands I frequently use at my work.

I use tshark more than [wireshark]('https://www.wireshark.org/') because
I frequently ssh to servers. Therefore, I have no GUI.

One of things I am yet to spend time to fix, is how to perform captures
as a user, not as root. I know there is a way, just never explored how.
Will post answer here when I figure it out.


### Define a Capture filter, output data to a file, print summary

In this example, I capture only DHCP packets during a switch bootup and
installation of software.


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
reference]('https://www.wireshark.org/docs/dfref/b/bootp.html')

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
