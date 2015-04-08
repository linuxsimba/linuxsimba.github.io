---
title: Debian QEMU PowerPC VM on Ubuntu 14.04
tags: ['powerpc', 'qemu', 'debian']
---

I want to build [omnibus](https://github.com/chef/omnibus-chef)  powerpc
packages. I don't own a Mac G4 or anything like that so QEMU is my best option.

### Downlaod Wheezy PowerPC VM

Someone at Debian does a nice job building one [Debian Wheezy powerpc Qcow2
image](https://people.debian.org/~aurel32/qemu/powerpc/).

### Install QEMU Debs


```
apt-get install qemu-system-ppc
apt-get install openbios-ppc
```

Then run
```
qemu-system-ppc -hda debian_wheezy_powerpc_standard.qcow2 -boot c -m 1024
```

QEMU came up, but I got nothing but a **blank screen** on the QEMU window.

### Get Latest OpenBios PPC file

The problem is that the `openbios-ppc` version Ubuntu 14.04 uses is old.

I got the latest `openbios-ppc` binary from
[qemu github site](https://github.com/qemu/qemu/tree/master/pc-bios)  and
installed it in `/usr/share/openbios`

### Setup a Reverse SSH session.

QEMU default networking does not allow you to ssh from the KVM host to the VM.
I am not sure why. When I do find the reason, I will link the answer to this
post.

Login on the QEMU console as with username ``root`` and password ``root``.
Start the Reverse SSH session. You can have the reverse ssh tunnel come by
default by installing ``autossh`` in ``/etc/rc.local``. [Configure public key SSH
authentication](https://macnugget.org/projects/publickeys/) between the VM and
KVM host as well if you want to use ``autossh``.


```
root@debian-powerpc:~# route -n
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         10.0.2.2        0.0.0.0         UG    0      0        0 eth0
10.0.2.0        0.0.0.0         255.255.255.0   U     0      0        0 eth0

root@debian-powerpc:~# ssh -fN -R5000:localhost:22 stanley@10.0.2.2 -p22
```

### From the KVM Host login into Debian PPC VM

```
$ ssh root@localhost -p 5000
```

Will detail my [omnibus](https://github.com/chef/omnibus-chef)
installation adventures on powerPC in a later post.


