---
title: Building Libvirt-vagrant Compatible Boxes
tags: ['qemu', 'kvm', 'libvirt', 'vagrant']
---

[Packer](http://www.packer.io) comes with a QEMU Builder. Its not well
documented, but thanks to [J.Toppins](https://github.com/jtoppins), I have a [git
repo that shows you how to build a Ubuntu and Jessie Libvirt compatible Vagrant Box
](https://github.com/skamithi/packer-libvirt-profiles)
<hr/>

> **This was the old post**. Originally created 25th Sept. This method still
> works. Just much longer.




### Download Packer

[Packer](http://www.packer.io) is a for creating machine images from a single source configuration.
It has a [QEMU builder](https://www.packer.io/docs/builders/qemu.html), but I found it too complicated

Packer ships in a zip package that contains binary files. Example of how
download packer and update the executable path search location.

```
mkdir $HOME/packer
cd $HOME/packer
wget https://dl.bintray.com/mitchellh/packer/packer_0.8.5_linux_amd64.zip
unzip packer_0.8_5_linux_amd64.zip
export PATH=$HOME/packer:$PATH
```

### Disable Libvirt and KVM (optional)

This step may not be required. Check if the KVM module and libvirt is running.

```
lsmod | grep kvm
ps -ef | grep libvirt-bin
```

If enabled, then disable these services

```
sudo service libvirt-bin stop
sudo rmmod kvm_intel kvm
```

### Download and enable virtualbox

```
sudo apt-get install virtualbox
service virtualbox start
```

### Download Chef Bento

[Chef/Bento](https://github.com/chef/bento)  contains packer config files for
the most popular linux distributions.

In this example I will use the ubuntu trusty configuration file.

```
cd $HOME/packer
git clone https://github.com/chef/bento
packer build bento/https://github.com/chef/bento/blob/master/ubuntu-14.04-amd64.json
```

The chef/bento package does provide virtualbox base boxes, but I like building from
scratch because it runs apt-get upgrade during the build process so I get the
latest updates. This is very helpful when building new large environments with
lots of ubuntu VMs. The time it takes to run ``apt-get upgrade``  on the new virtual
environment is greatly shortened because the box image has the latest updates.

> **Note**: This process requires a PC with a GUI. Part of the process
> spins up a Virtualbox console and executes config in it. It does not appear to
> be headless and I am not sure how to run packer in Virtualbox headless mode

If you do not have a GUI, then I would suggest just download the base box you
want and proceed to the next step

Packer gives its generated boxes weird names. Not sure how to remedy this and
give it some sane names.  So in my case, it created a box called
``__unset_box_basename__.virtualbox.box``


### Vagrant mutate from Virtualbox provider to libvirt KVM provider

Install [Vagrant](http://www.vagrantup.com/downloads.html) if you have not done so already

Install the [vagrant mutate plugin](https://github.com/sciurus/vagrant-mutate) and apply it to the base box created

```
vagrant plugin install vagrant-mutate
vagrant mutate __unset_box_basename__.virtualbox.box libvirt
```

After this is completed, I would suggest rename the box created

```
$ cd $HOME/.vagrant.d/boxes
$ mv __unset_box_basename__.virtualbox trusty64
$ vagrant box list | grep trusty
   trusty64        (libvirt, 0)
```

### Disable Virtualbox and Install/Enable Libvirt

These steps disable Virtualbox , install libvirt, if it is not installed and
enable KVM.

```
sudo service virtualbox stop
sudo apt-get purge virtualbox
sudo apt-get install libvirt-bin qemu-kvm
sudo modprobe kvm_intel
sudo service libvirt-bin start

```
## Boxes Available from LinuxSimba

For my convenience I save my favorite base boxes from libvirt on
[linuxsimba.com](http://linuxsimba.com).
I will update this list from time to time, and
may eventually get it listed on [vagrantboxes.es](http://vagrantboxes.es)

* [Ubuntu 14.04](http://linuxsimba.com/vagrantbox/ubuntu-trusty.box)
* [Jessie 8](http://linuxsimba.com/vagrantbox/debian-jessie.box)
* [Cumulus Linux VM](http://linuxsimba.com/vagrantbox/cumulus-253.box)

* [All Linuxsimba KVM Vagrant Boxes](http://linuxsimba.com/vagrant.html)

Right click the above link and run

```
vagrant box add [paste_saved_link] -n [name_you_want_to_give_box]
```

Ubuntu trusty download example

```
vagrant box add http://linuxsimba.com/vagrantbox/ubuntu-trusty.box -n trusty64
```




