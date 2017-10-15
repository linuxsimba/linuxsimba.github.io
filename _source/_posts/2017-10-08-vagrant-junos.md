---
title: "Building JunOS Vagrant Setups using Libvirt"
tags: ['juniper', "network", "automation"]
---

Juniper provides a free [QFX10k](https://www.juniper.net/us/en/products-services/switching/qfx-series/qfx10000/) VM with limited features available from hashicorp Atlas website.
I am an avid support of vagrant and the [vagrant-libvirt](https://linuxsimba.com/vagrant-libvirt-install) component. Unfortunately Juniper only officially release the vqfx VM for vagrant-virtualbox.

Vagrant-libvirt has the advantage of using KVM tech which has a smaller memory footprint then Virtualbox. Also [QEMU can use UDP tunnels to create point to point connections](https://linuxsimba.com/qemu-tunnel-types) between VMS. This means it is possible to build a QEMU environment between 2 or more baremetal devices.

This blog post goes over how to create a Vagrant libvirt box for Vqfx10k.

## Install Vagrant Libvirt
I have a post on [how to install vagrant-libvirt](https://linuxsimba.com/vagrant-libvirt-install). Also the [official vagrant-libvirt github site](https://github.com/vagrant-libvirt/vagrant-libvirt) has further details.

## Install virtualbox
Install Virtualbox via the Linux system package manager (apt/yum). After the conversion of the fixed VM to a libvirt format, you can delete all Virtualbox system packages, if you want.

## Download Virtuabox Vqfx10k Box

```
vagrant box add juniper/vqfx10k-re
==> box: Loading metadata for box 'juniper/vqfx10k-re'
    box: URL: https://vagrantcloud.com/juniper/vqfx10k-re
==> box: Adding box 'juniper/vqfx10k-re' (v0.2.0) for provider: virtualbox
    box: Downloading: https://vagrantcloud.com/juniper/boxes/vqfx10k-re/versions/0.2.0/providers/virtualbox.box
==> box: Successfully added box 'juniper/vqfx10k-re' (v0.2.0) for 'virtualbox'!
```

## Download HashiCorp's Packer

Packer is a single precompiled binary written in Go. [Just download it](https://www.packer.io/docs/install/index.html) and place it in ``/usr/local/bin``.


## Git clone vagrant-libvirt-junos repo and create a usable VM for vagrant-libvirt

The problem with the Virtualbox vqfx10k is that the ``em0``, the management interface for vqfx10k, is already assigned a IP address of ``10.0.2.15``. If you take this Virtualbox OVF, and convert it to a QCOW2 image, and boot it up, ``em0`` fails to pick up an IP address from the dnsmasq server running on the ``vagrant-libvirt`` Linux bridge created by vagrant-libvirt.
The problem is that the Vqfx10k VM continously sends out a DHCPREQUEST instead of sending a DHCPDISCOVER. So DNSMasq ignores the request and nothing happens.

```
root@vqfx-re> show dhcp client binding
IP address        Hardware address   Expires     State      Interface
10.0.2.15         00:0f:81:61:36:00  0           REQUESTING em0.0
```

I suspect the Juniper builders of the Virtualbox VM did not take this problem into account because it always works with Virtualbox.


To clear this run the command ``clear  dhcp client binding all`` from the console.

The Vqfx10k Virtualbox VM already has a vagrant user with the insecure Vagrant key, so none of that needs to be configured.

After running the command to clear the DHCP client bindings then the Vqfx10k VM now has a working DHCP management Interface

```
root@vqfx-re> show dhcp client binding
IP address        Hardware address   Expires     State      Interface
0.0.0.0           00:0f:81:61:36:00  0           INIT       em0.0
```

This is where Packer comes to play. It supports the ability to load an existing OVF and run boot commands (console commands) to fix the issue and save a new Vagrant Box. So this is what my repo does.

```

git clone https://github.com/linuxsimba/libvirt-network-switches
cd libvirt-network-switches
vagrant box add juniper/vqfx10k-re
cp -rv $HOME/.vagrant.d/boxes/juniper-VAGRANTSLASH-vqfx10k-re/0.2.0/virtualbox/* .
packer build fix_junos_dhcp.json

```
A window should appear showing the console of the VM and the console commands executed the fix the issue.  After the fixed VM is built, add the fixed Vagrant Box into your vagrant box repository. Then convert the OVF to a QCOW2 so it can work with vagrant-libvirt. Use the vagrant-mutate plugin to achieve this.

```
vagrant plugin install vagrant-mutate
vagrant box add boxes/junos_dhcp_fixed.box --name "vqfx10k-fixed-dhcp"
vagrant mutate vqfx10k-fixed-dhcp libvirt
```

## Use the Fixed Vagrant Box in a Vagrantfile.

Here is an example of a vagrant-libvirt compatible Vagrantfile using the fixed Vagrant Box.

{%gist 3c92a611cd27f42874c5d5e8e56e005e %}

Start up Vagrant using the libvirt provider and the above Vagrantfile

```
vagrant up --provider libvirt
...
....
.....

vagrant ssh

  --- JUNOS 15.1X53-D63.9 built 2017-04-01 20:45:26 UTC
  {master:0}
  vagrant@vqfx-re>
```

## Troubleshooting

If you get an error like this when executing ``packer`` ...

```
Build 'virtualbox-ovf' errored: Error starting VM: VBoxManage error: VBoxManage: error: VT-x is being used by another hypervisor (VERR_VMX_IN_VMX_ROOT_MODE).
VBoxManage: error: VirtualBox can't operate in VMX root mode. Please disable the KVM kernel extension, recompile your kernel and reboot (VERR_VMX_IN_VMX_ROOT_MODE)
VBoxManage: error: Details: code NS_ERROR_FAILURE (0x80004005), component ConsoleWrap, interface IConsole

```

Look for all KVM instances running and kill them. Check ``virsh list`` command and/or run ``ps -ef | grep qemu`` to locate all the KVM Virtual machines.
