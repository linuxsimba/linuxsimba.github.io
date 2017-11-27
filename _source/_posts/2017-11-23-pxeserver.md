---
title: "Simple PXE Server"
tags: ["vagrant", "pxe"]
---

When submitting a patch to add Vagrant Halt capabilities to Vagrant-libvirt,the maintainer asked me to test the patch against a PXE VM.

So I put together a pxe server Ansible role to achieve this and rolled it into a vagrant-libvirt setup. Its a very simple PXE server. Its just DNSMasq and Nginx, both lightweight apps. Maybe one day this can be built as a docker-compose app as well.

## Topology

```
+---------------+             +----------------+
|               |             |                |
|    PXE        |             |    PXE         |
|    Server     |eth1       eth0   VM          |
|               +-----------+ |                |
|               |             |                |
|               |             |                |
+-----eth0------+             +----------------+
        |                              |
+-----------+------------------------------+------------+
|                                                       |
|               Vagrant hyperVisor                      |
+-------------------------------------------------------+

```

## Requirements

* Vagrant-Libvirt
* 10G Disk free
* 2 GB RAM free
* Ansible 2.4+

## Installation

```
# git clone https://github.com/linusimba/ansible-pxeserver
# cd ansible-pxeserver
# vagrant up pxeserver pxevm --no-parallel
```

## Logging into PXE Booted VM

SSH into the pxeserver. Sudo to root, then ssh to ssh root@10.1.1.10 to access the VM. Root password on the PXE VM is not enabled.

```
vagrant_hypervisor:$ vagrant ssh pxeserver

vagrant@pxeserver:~$ sudo su -

root@pxeserver:~# ssh root@10.1.1.10

root@pxetestvm:~#
```

## Limitations

Only supports Ubuntu. One day will support Centos as well.
