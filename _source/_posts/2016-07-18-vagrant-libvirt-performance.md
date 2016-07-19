---
title: Vagrant Libvirt Performance and Operations
tags: ['vagrant', 'libvirt']
---

Simulating an Openstack environment that consists of 12 Openstack nodes and 4
switches. When I first started, performance was horrible. Here are some the
things I did to improve performance. Still learning, so if anyone has any tips, please share.


## Tweak 1: Convert a simple dotviz file to a complicated messy looking Vagrantfile

A Vagrantfile is not a simple document to generate. Really! It is the kind of file you want a computer to create. Thank goodness, there is a cool opensource
tool - [topology-generator](https://github.com/CumulusNetworks/topology_converter) - to do that for you.


## Tweak 2: Increase UDP Buffers

A large reliable vagrant-libvirt setup makes heavy use of [UDP
sockets](http://linuxsimba.com/qemu-tunnel-types). Configuring network buffers
to the maximum values helps a lot.  Here is a [good reference](http://www.cyberciti.biz/faq/linux-tcp-tuning/).


## Tweak 3: Use the virtio_net driver where you can.

The performance of the virtio\_net driver is just miles ahead of the `e1000` VM NIC drivers.
The virtio_net driver is not perfect. By default, the virtio_net NIC speed to `-1`. But it [can be
changed](https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1581132)! I would love to know how to set it to a particular speed by default using a kernel cmdline argument.

Here is how I set the virtio_net enabled NIC speed. I need a better way. If someone knows a better way, please share.

```
auto ens6
iface ens6 inet manual
  description bond member
  bond-primary ens6
  bond-master bond0
  post-up ethtool -s $IFACE speed 10000 duplex full
auto ens7
iface ens7 inet manual
  description bond member
  bond-primary ens6
  bond-master bond0
  post-up ethtool -s $IFACE speed 10000 duplex full
```

This config is not perfect. Ethtool does not kick in all the time, resulting in inconsistent bonds or connectivity issues. For all nodes
that need stable network bonding, I stick with the `e1000` NIC driver.

## Tweak 4: Use kernel 4.x and higher

Nested Virtualization works so much better on a 4.x kernel than a 3.x Linux kernel.
I am not sure why. Here is [a great video](https://www.youtube.com/watch?v=ISKfq66vTs8) to teach you more about nested virtualization.


That is all I have for now.

If I find more ways to improve vagrant-libvirt performance I will share it on this post.


## Results so far:

A Level 2 Windows Server 2012 VM running in a Level 1 Linux VM ping performance

```
 $ ping 192.168.8.76
PING 192.168.8.76 (192.168.8.76) 56(84) bytes of data.
64 bytes from 192.168.8.76: icmp_seq=1 ttl=127 time=32.0 ms
64 bytes from 192.168.8.76: icmp_seq=2 ttl=127 time=13.4 ms
64 bytes from 192.168.8.76: icmp_seq=3 ttl=127 time=2.75 ms
64 bytes from 192.168.8.76: icmp_seq=4 ttl=127 time=2.57 ms
64 bytes from 192.168.8.76: icmp_seq=5 ttl=127 time=3.02 ms
64 bytes from 192.168.8.76: icmp_seq=6 ttl=127 time=7.05 ms
64 bytes from 192.168.8.76: icmp_seq=7 ttl=127 time=3.10 ms
64 bytes from 192.168.8.76: icmp_seq=8 ttl=127 time=2.88 ms
```

Not bad I think. Originally the latency averaged 30ms



