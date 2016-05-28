---
title: TinyCore Linux Vagrant Libvirt Box Build Notes
tags: ['packer','tinycore', 'vagrant']
---

Have a need for tiny VMs for my Vagrant environment to simulate devices I do not care about. For example: printers.

[TinyCore Linux](http://tinycorelinux.net/) comes in really handy. It has a very small footprint - 256MB Disk , 64MB RAM.

This is the Vagrant  Libvirt Box build process for Tiny Core Linux.

### Remaster TinyCore Linux ISO
The stock Tiny Core Linux ISO does not have SSH enabled or a user that the Packer can use to build the Vagrant Box.  [Github User BugRoger](https://github.com/BugRoger/tinycorelinux-packer-image) provides an elegant solution to solve this.

The linuxsimba fork of this repo changes the username from _packer_ to _vagrant_.
It  adds Tiny Core Linux apps like iproute2 and other useful things for my vagrant simulations.  The new ISO is called ``tinycore-vagrant.iso``

```
sudo apt-get install squashfs-tools advancecomp

git clone https://https://github.com/linuxsimba/tinycorelinux-packer-image

cd tinycorelinux-packer-image

sudo ./remaster.sh

ls tinycore*
    tinycore-vagrant.iso
```

### Build the Vagrant Box using Packer
> assumes you have [Packer](https://www.packer.io/downloads.html) already installed

The Vagrant Box configures persistent storage for TC apps installed (.tcz) and
home directories for the _tc_ & _vagrant_ users.

```

git clone https://github.com/linuxsimba/packer-libvirt-profiles

cd packer-libvirt-profiles

cp ../tinycorelinux-packer-images/tinycore-vagrant.iso .

md5sum tinycore-vagrant.iso
   584e00138eea9938d13a8156ab21355a

echo '{"mirror_directory": "./", "iso_checksum": "584e00138eea9938d13a8156ab21355a", "iso_checksum_type": "md5"}' > vars.json

packer build -var-file vars.json tinycore-7.0.json

vagrant box add builds/tinycore-7.0.libvirt.box --name tc

```

If you want to use it in your Vagrantfile without customizing the build,  point the ``box.url`` to linuxsimba.com libvirt box repo.

```
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "http://linuxsimba.com/vagrantbox/tinycore-7.0.libvirt.box"
  config.vm.synced_folder '.', '/vagrant', :disabled => true
end

```

