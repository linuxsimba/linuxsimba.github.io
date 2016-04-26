---
title: Network Bonding in a Vagrant-Libvirt Environment
tags: ['bonding', 'vagrant']
---

Trying to configure a network bond in
[vagrant-libvirt](https://github.com/pradels/vagrant-libvirt) environment?

Getting an error like this on the Linux host?

```
bond0: Warning: No 802.3ad response from the link partner for any adapters in the bond
```

If you get this error, confirm that the port speed is not available in sysfs.

<pre>
$ ip link show eth1

3: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000
    link/ether 52:54:00:27:16:f8 brd ff:ff:ff:ff:ff:ff

$ cat /sys/class/net/eth1/speed

<strong>cat: /sys/class/net/eth1/speed: Invalid argument</strong>
</pre>


The fix is simple. Get the interface to report a speed. Change the vagrant libvirt default QEMU NIC driver, ``virtio``, to another
driver that reports a speed setting like `e1000`.

<pre>
...
......
config.vm.define :compute1 do |node|
    node.vm.hostname = "compute1"
    node.vm.provider :libvirt do |domain|
      domain.memory = 512
      <strong>domain.nic_model_type = 'e1000'</strong>
    end
    node.vm.box = 'trusty64'
...
.....
</pre>

Reload the vagrant setting using ``vagrant reload compute1`` and
the bond will form. Unfortunately LACP debugs in userspace do not exist. Only
thing you can do to troubleshoot LACP on a Linux system, from a system administration perspective,
is a sniffer trace, and reading [Linux kernel source
code](https://github.com/torvalds/linux/blob/master/drivers/net/bonding/bond_3ad.c).
