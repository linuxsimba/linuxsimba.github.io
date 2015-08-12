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

vagrant libvirt provider is rapidly evolving. I would suggest compiling from source. Here goes

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
Switch back to the System Ruby, set it as the default, and install the compiled ruby gem into the vagrant environment. The gem version number isn't different for the dev version or stable version. But vagrant knows the difference.

```
$ rvm use system --default
$ vagrant plugin install pkg/vagrant-libvirt-0.0.30.gem
$ vagrant plugin list
vagrant-libvirt (0.0.30)
  - Version Constraint: 0.0.30
vagrant-share (1.1.4, system)

```

### Install Vagrant Boxes

Download and install a KVM Vagrant box. I have 2 available for download.

* [Ubuntu 14.04.2 Minimal Install]()
* [Debian Jessie Minimal Install]()

Other KVM boxes can be found at [vagrantboxes.es](http://vagrantboxes.es). Some take forever to download. Others just do not work well. If my boxes take a long time to download please let me know and maybe sugest where I can post these for free or low cost and improve download speeds. The [main Vagrant box site](https://atlas.hashicorp.com/boxes/search)  doesn not seem to support uploading a KVM Vagrant box.

```
wget [blah] -o trusty64.box
$ vagrant box add ./trusty64.box --name "trusty64"
```

Verify the box is installed

```
$ vagrant box list
trusty64 (libvirt, 0)
```


### Create a 2 VM Vagrant file

Create a 2 VM Vagrant file using libvirt very isolated network config. Basically this is a bridge with no DNSMASQ running or NAT applied. This type of connection is suitable for IP connectivity. LLDP/BPDUs will be consumed by the host.

#### Topology
![enter image description here](https://lh3.googleusercontent.com/mLfqQBP0gp31_5burudaA9cbV6AT1fnSJT5Zcz7dleE=s0 "vagrant-libvirt-topology.png")

#### Vagrant Configuration

{% gist skamithi/ea5b85ee4b01c879abc8 %}
