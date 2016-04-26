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

If you get this error, confirm that first of all the port speed is not available

<pre>
<code>
$ ip link show eth1

3: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000
    link/ether 52:54:00:27:16:f8 brd ff:ff:ff:ff:ff:ff

$ cat /sys/class/net/eth1/speed

<strong>cat: /sys/class/net/eth1/speed: Invalid argument</strong>
</code>
</pre>


The fix is simple. Change the QEMU interface driver from ``virtio`` to another
driver that reports a speed setting like `e1000`.

<pre>
<code>
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
</code>
</pre>

Reload the vagrant setting using ``vagrant reload compute1`` and
the bond will form. Unfortunately LACP debugs in userspace do not exist.
So I figured this one out by reading the Linux source code!
