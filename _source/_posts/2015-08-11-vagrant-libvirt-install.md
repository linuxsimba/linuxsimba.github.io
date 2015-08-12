---
title: Vagrant Libvirt Install on Ubuntu 14.04
tags: ['vagrant', 'libvirt', 'ruby', 'qemu']
---

Got a question on how I setup [vagrant-libvirt](https://github.com/pradels/vagrant-libvirt). This is my most basic setup.

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
$ sudo apt-get install qemu-kvm libvirt-bin
$ sudo adduser $USER libvird
```

### Install vagrant-libvirt

vagrant libvirt provider development is rapidly evolving. I would suggest installing from source.

#### install RVM to compile vagrant-libvirt
Based on the [rvm.io](http://rvm.io) instructions its simple to install the required ruby-2.1 into your user directory

```
$ sudo apt-get install curl
$ gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3
$ \curl -sSL https://get.rvm.io | bash -s stable --ruby=2.1
```

Close the SSH session and log back in to activate RVM. There are other ways to do this without logging out, but I found this to be easiest to do.

You can confirm its working by running ``rvm list``

```
$ rvm list

rvm rubies

=* ruby-2.1.5 [ x86_64 ]

# => - current
# =* - current && default
#  * - default

```

#### git install vagrant-libvirt

```
$ sudo apt-get install git
$ git clone https://github.com/pradels/vagrant-libvirt
```

#### Switch to RVM version 2.1 and compile vagrant-libvirt

Install libvirt-dev and compile the libvirt vagrant provider from the latest version found on its master branch.

```
$ sudo apt-get install libvirt-dev
$ rvm use ruby-2.1
$ cd vagrant-libvirt
$ bundle install
$ bundle exec rake build
Your Gemfile lists the gem vagrant-libvirt (>= 0) more than once.
You should probably keep only one of them.
While it's not a problem now, it could cause errors if you change the version of just one of them later.
vagrant-libvirt 0.0.30 built to pkg/vagrant-libvirt-0.0.30.gem.


```

### install the most recent version of vagrant-libvirt
Switch back to the System Ruby, set it as the default, and install the compiled
ruby gem into the vagrant environment. The gem version number is not different for the dev version or stable version. But vagrant knows the difference.

```
$ rvm use system --default
$ vagrant plugin install pkg/vagrant-libvirt-0.0.30.gem
$ vagrant plugin list
vagrant-libvirt (0.0.30)
  - Version Constraint: 0.0.30
vagrant-share (1.1.4, system)

```

### Install Vagrant Boxes

A Vagrant box is a tar archive with 3 files in it.

* base VagrantFile
* metadata.json
* QCOW2 image

A few native KVM Vagrant Boxes are available at
[vagrantboxes.es](http://vagrantboxes.es).

Use the `vagrant box add` command to download a box either from a local file
system or from a URL.

```
$ vagrant box add https://vagrant-kvm-boxes.s3.amazonaws.com/precise64-kvm.box --name "trusty64"
```

Verify the box is installed

```
$ vagrant box list
trusty64 (libvirt, 0)
```

 I prefer to build my own from
scratch. A [few people have
blogged](https://www.google.com/search?q=vagrant%20mutate%20blog) about how to
do this. Unfortunately none cover the case on what to do when you have
virtualbox and KVM software installed at the same time. The two are mutually
exclusive and you have to turn one off one, to get the other to work. Maybe I will
blog about my steps in the near future.



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
