---
title: Debian QEMU PowerPC VM on Ubuntu 14.04
tags: ['powerpc', 'qemu', 'debian']
---

I want to build [omnibus](https://github.com/chef/omnibus-chef)  powerpc
packages. I don't own a Mac G4 or anything like that so QEMU is my best option.

To do this I downloaded a [Debian Wheezy powerpc Qcow2
image](https://people.debian.org/~aurel32/qemu/powerpc/).

Next I installed the necessary QEMU files

```
apt-get install qemu-system-ppc
apt-get install openbios-ppc
```

Then I ran

```
qemu-system-ppc -hda debian_wheezy_powerpc_standard.qcow2 -boot c -m 1024
```

QEMU came up, but I got nothing but a **blank screen** on the QEMU window.

The problem is that the `openbios-ppc` version Ubuntu 14.04 uses is old.

I got the latest `openbios-ppc` binary from
[qemu github site](https://github.com/qemu/qemu/tree/master/pc-bios)  and
installed it in `/usr/share/openbios`

All is good now! Will detail my [omnibus](https://github.com/chef/omnibus-chef)
installation adventures on powerPC in a later post.


