---
title: Backup Server using a Customized Debian Live CD OS
tags: ['debian', 'livecd']
---

> NOTE (Jan 2016): There has been [some squabble in
> Debian](https://lists.debian.org/debian-live/2015/11/msg00053.html) about the Debian Live CD project. Its
> link was cleaned out..so the links referenced in this doc do not work. Once
> the Debian Live CD project is spin out and it has its own website, I will
> change my reference links. For now all the links to Debian Live CD point the epub documentation
> I downloaded a while ago. The doc is well written. Probably one of the best
> I have seen for an open source project.

## Goal
Convert an old Shuttle PC with 2 1TB Disks into a Backup server and so much more.

The PC only has slots for two Hard Drives, and I want to utilize the 2 1 TB disks as members in a RAID-1 Array, my only choice is to load the software needed on a USB Stick.

After much research, I decided to go with the [Debian Live CD
Project](http://linuxsimba.com/vagrantbox/debian_live_manual.epub)

## Building the Debian Live CD Environment

In order to create my custom USB drive image, I first setup my Ubuntu 14.04 Laptop with the Debian Live CD development environment.

Debian Live CD asks you to install 2 programs

 * [live-build](http://linuxsimba.com/vagrantbox/debian_live_manual.epub)
 * [live-boot](http://linuxsimba.com/vagrantbox/debian_live_manual.epub)

There is a *live-config* program as well but I was not able to build the deb package for this from the git repository.

### Git clone live-build and run build the deb

*live-build* contains the components to build a live system from a configuration directory.

```
$ git clone https://anonscm.debian.org/git/debian-live/live-build.git
$ cd live-build
$ dpkg-buildpackage -b -uc -us
$ cd ..
```

### Git clone live-boot and build the deb
*live-boot* is a collection of scripts that enables the building of USB Stick images. So I definitely need to install this

```
$ git clone https://anonscm.debian.org/git/debian-live/live-boot.git
$ cd live-boot
$ dpkg-buildpackage -b -uc -us
$ cd ..
```
### Why I cannot install live-config?
*live-config* is a collections of scripts that configure a live system automatically. I cannot install it on Ubuntu 14.04 because it requires ``dh-systemd`` in the build process, which Ubuntu 14.04 does not support. Not sure if its a good idea to muck around with the ``debian/control`` files and remove that dependency.


### Install Debian Live Project Debs

```
$ ls *.deb
live-boot_5.0~a5-1_all.deb  live-boot-doc_5.0~a5-1_all.deb  live-boot-initramfs-tools_5.0~a5-1_all.deb live-build_5.0~a11-1_all.deb
$ sudo dpkg -i live*.deb
```

## Building the Custom USB Drive Based Debian OS

I created a [github repo](http://github.com/linuxsimba/backup_server_live_cd). There are 2 main directories.
* `auto`: this has the basic livecd build configuration options
* `config`: This directory has the base config files for a debian jessie live cd, with a few changes

### set the boot timeout
This is set in  [config/includes.binary/isolinux/isolinux.cfg](https://github.com/linuxsimba/backupserver_debian_livecd/blob/master/config/includes.binary/isolinux/isolinux.cfg)

### define the list of additional packages to install

This is set in [config/package-lists/my.list.chroot](https://github.com/linuxsimba/backupserver_debian_livecd/blob/master/config/package-lists/my.list.chroot)

One of the packages, `mdadm` requires a debconf preseed. This is found in [config/preseed/mdadm.cfg.chroot](https://github.com/linuxsimba/backupserver_debian_livecd/blob/master/config/preseed/mdadm.cfg.chroot)

### set the default  username
This is set in the [auto/config](https://github.com/linuxsimba/backupserver_debian_livecd/blob/master/auto/config) file

### set ssh public keys for passwordless access

This is accomplished by adding the public keys to [config/includes.chroot/home/enable/.ssh/authorized_keys](https://github.com/linuxsimba/backupserver_debian_livecd/tree/master/config/includes.chroot/home/enable/.ssh) and then setting the file permissions properly in [config/includes.chroot/lib/live/config/2000-set-home-directory-permission](https://github.com/linuxsimba/backupserver_debian_livecd/blob/master/config/includes.chroot/lib/live/config/2000-set-home-directory-permission)

### setup already configured RAID array to be automatically mounted and map to a directory
When setting up the Shuttle PC, I used a generic Debian Live CD, to configure the RAID array. RAID-1, using steps [similar to this website](http://www.ducea.com/2009/03/08/mdadm-cheat-sheet/). It would be super awesome to have this custom live cd do it, but I do not have time to build and test that software.

To mount the RAID array, I take a sledge hammer approach and modify [config/includes.chroot/etc/rc.local](https://github.com/linuxsimba/backupserver_debian_livecd/blob/master/config/includes.chroot/etc/rc.local). I really should create a sytemctl service that runs after mdadm executes. But I do not have time to do that. This works for now.

## Installing the Customized Debian Live CD onto a USB Stick

After installing the [github repo](http://github.com/linuxsimba/backup_server_live_cd), run

```

sudo lb config
sudo lb build

```

The USB drive used was unformatted using [gparted](http://gparted.org/). I just removed all partitions and saved the changes.

After the build, the iso-hybrid image created was directly copied to the `/dev/sdX` device matching the USB disk. In this case it is `/dev/sdc`.

```
cp live-image-amd64.hybrid.iso  /dev/sdc
```

That is it! When the USB drive was plugged into the Shuttle Server, it booted up without any intervention. The DHCP server was set to always assign the server the same IP.
The ssh authorized_keys worked as expected and passwordless authentication works from my laptop.
