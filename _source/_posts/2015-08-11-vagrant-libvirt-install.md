---
title: Vagrant Libvirt Install on Ubuntu 14.04
tags: ['vagrant', 'libvirt', 'ruby', 'qemu']
---

Got a question on how I setup [vagrant-libvirt](https://github.com/vagrant-libvirt/vagrant-libvirt). This is my most basic setup.

> The steps I describe are only **tested and used on Ubuntu 14.04**

### Install Vagrant

Easy enough!  [Install the deb](http://www.vagrantup.com/downloads.html)

```
$ wget https://dl.bintray.com/mitchellh/vagrant/vagrant_1.7.4_x86_64.deb
$ sudo dpkg -i vagrant_1.7.4_x86_64.deb
```
### Install libvirt and qemu-kvm

Follow the [Ubuntu Libvirt Guide](https://help.ubuntu.com/lts/serverguide/libvirt.html)

```
$ sudo apt-get update
$ sudo apt-get install qemu-kvm libvirt-bin libvirt-dev
$ sudo adduser $USER libvirtd
```


### Install vagrant-libvirt gem
All the Changes, I submitted,  to setup multiple VMs using the unicast UDP tunnel support is
now in version 0.0.31 :)

This step may require ``libvirt-dev`` deb package be installed.

```
$ vagrant plugin install vagrant-libvirt
$ vagrant plugin list
vagrant-libvirt (0.0.31)
vagrant-share (1.1.4, system)
```

### Install Vagrant Boxes

A Vagrant box is a tar archive with 3 files in it.

* base VagrantFile
* metadata.json
* QCOW2 image


LinuxSimba provides the [Ubuntu and Jessie KVM Libvirt
Boxes](http://linuxsimba.com/vagrant.html)

A few native KVM Vagrant Boxes are also available at
[vagrantboxes.es](http://vagrantboxes.es). But these, to me, are less reliable.

Use the `vagrant box add` command to download a box either from a local file
system or from a URL.

```
$ vagrant box add http://linuxsimba.com/vagrant/ubuntu-trusty.box --name "trusty64"
```

Verify the box is installed

```
$ vagrant box list
trusty64 (libvirt, 0)
```

I prefer to build my own from scratch. Here is [my blog post about that subject]({% post_url 2015-08-22-building-qcow-vagrant-box %}).



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
