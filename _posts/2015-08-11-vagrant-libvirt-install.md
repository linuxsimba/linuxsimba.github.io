---
title: Vagrant Libvirt Install on Ubuntu 14.04/16.04
tags: ['vagrant', 'libvirt', 'ruby', 'qemu']
---

> Updated June 2016

Got a question on how I setup [vagrant-libvirt](https://github.com/vagrant-libvirt/vagrant-libvirt). This is my most basic setup.


### Install Vagrant

Easy enough!  [Install the deb](http://www.vagrantup.com/downloads.html)

```
wget https://releases.hashicorp.com/vagrant/1.8.4/vagrant_1.8.4_x86_64.deb
sudo dpkg -i vagrant_1.8.4_x86_64.deb
```
### Install libvirt and qemu-kvm

Follow the [Ubuntu Libvirt Guide](https://help.ubuntu.com/lts/serverguide/libvirt.html)

```
$ sudo apt-get update
$ sudo apt-get install qemu-kvm libvirt-bin libvirt-dev
$ sudo adduser $USER libvirtd
```


### Install vagrant-libvirt gem

This step may require ``libvirt-dev`` deb package be installed.

```
$ vagrant plugin install vagrant-libvirt
$ vagrant plugin list
vagrant-libvirt (0.0.33)
```

### Install Vagrant Boxes

A Vagrant box is a tar archive with 3 files in it.

* base VagrantFile
* metadata.json
* QCOW2 image


You can also build your own Vagrant box very easily using [Packer](https://www.packer.io/downloads.html) and Packer build templates found in [chef/bento github repo](https://github.com/chef/bento).

#### Example: using a PC with a Monitor

```
git clone https://github.com/chef/bento
cd bento
packer build -only qemu ubuntu-14.04.amd64.json
vagrant box add builds/ubuntu-14.04.libvirt.box --name "trusty64"
```

#### Example: using a Server with No Monitor Access (headless)

```
git clone https://github.com/chef/bento
cd bento
packer build -only qemu -var "headless=true" ubuntu-14.04.amd64.json
vagrant box add builds/ubuntu-14.04.libvirt.box --name "trusty64"
```

Verify the box is installed

```
$ vagrant box list
trusty64 (libvirt, 0)
```

### Create a 2 VM Vagrant file

Create a 2 VM Vagrant file using libvirt, with their `eth1` addresses in a
[very isolated network
config](http://wiki.libvirt.org/page/VirtualNetworking#Isolated_mode). Basically
this is a bridge with no DNSMASQ running or NAT applied. This setup is useful
for connecting VM NICs via IP. It is not suitable for L2 config like point to
point VM links that need BPDUs or other types of L2 protocols to flow between
the VMs.   LLDP frames/BPDUs are consumed by the host.
``eth0`` on the VMs is managed by vagrant code and it automatically assigns it
to a [bridge with DNSMASQ and
NAT](http://wiki.libvirt.org/page/VirtualNetworking#NAT_mode) applied.

#### Topology
![Simple breakdown of libvirt topology
here](https://lh3.googleusercontent.com/LzAXNckJ9tvjMVb1MFnABPZ-B1RfQ8U0xhgdUMY05vU=s0
"vagrant-libvirt-topology.png")

#### Vagrant Configuration

{% gist skamithi/ea5b85ee4b01c879abc8 %}
