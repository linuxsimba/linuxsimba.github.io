---
title: Notes on Building Mirantis Fuel Vagrant Box
tags: ['mirantis', 'openstack', 'packer', 'vagrant']
---

These are the notes on how the Mirantis Fuel Vagrant Box was built.
For details on the install, go to the [previous post]({% post_url 2016-02-06-mirantis-fuel-vagrant-libvirt %}).

[HashiCorp's Packer](https://www.packer.io/downloads.html) is a cool tool. Take any ISO, and in a few hours, you can transform the ISO into a Vagrant Box.

After running through the entire install of Mirantis Fuel manually using
libvirt's [virt-manager](https://virt-manager.org/), _and screen capturing the
output using gtk-recordmydesktop_, it was determined that the following files
were relevant to the Vagrant Box creation.

```
  - isolinux/isolinux.cfg
  - ks.cfg
```

``isolinux/isolinux.cfg`` defined what the kernel boot commands are by default.
packer was configured to delete this as it hard codes the IP address of the eth0
interface. It has some undesirable effects during the Vagrant Box build process.
Packer was configured to amend the boot command variables, so the final
boot command was the output shown below. All Fuel setup menu interactivity was disabled as well by setting
the ``showmenu`` option to ``no``.

```
vmlinuz initrd=initrd.img hostname=fuel.domain.tld showmenu=no admin_interface=eth1 dhcp_interface=eth0 text ks=http://10.0.2.2/mirantis-7/ks.cfg
```

The ``HTTPIP`` and ``HTTPPort`` config is Packer magic. When packer executes it creates
a temporary HTTP server that the QEMU VM can access to get to its kickstart
config in the ``http`` directory of the packer build repo.


``ks.cfg``, the kickstart file, was amended to add a Vagrant Box user, delete
the code that configures what Fuel calls the `admin_interface`.

The [centos-6](https://github.com/chef/bento/blob/master/centos-6.7-x86_64.json) packer build script was used as the starting point for the
mirantis Fuel packer build script.

When all was configured, the following ``packer`` command was executed, and on a
Intel I5, 4 GB server, it took about 30 minutes to build the Vagrant Box.

The final box image for Mirantis-7 Fuel Vagrant Box was about 4.7GB. Packer
does some compression and removal of _unnecessary_ packages.

The [linuxsimba packer template repo](http://github.com/linuxsimba/packer-libvirt-profiles
) contains an [example Vagrantfile](http://github.com/linuxsimba/packer-libvirt-profiles/blob/master/vagrantfile_examples/Vagrantfile.mirantis) to use to
setup the Mirantis OpenStack setup.

This Vagrantfile hard codes the ``eth0`` MAC
address of the openstack nodes. This is because Mirantis Fuel assumes,
correctly, that the PXE MAC for a particular server should not change. So as one creates and destroys the
openstack nodes using `vagrant destroy/up`, Mirantis Fuel will not get confused and think its a new server.

The Vagrant Box does not have the docker containers needed for Fuel to work.
The script to generate the docker containers is run as a Vagrantfile provision
script during a ``vagrant up`` run.

The Vagrant Box therefore, is relatively small in size, and easier to distribute
than one that is loaded with all the Fuel docker containers. The box size is
about 4.7GB.


> Not sure if the Vagrant Box can be [posted on this site](/vagrant.html). I am going to
ask Mirantis if that is okay.
