---
title: "Building JunOS Vagrant Setups using Libvirt"
tags: ['juniper', "network", "automation"]
---

Juniper provides a free [QFX10k](https://www.juniper.net/us/en/products-services/switching/qfx-series/qfx10000/) VM with limited features available from the Hashicorp Atlas website.
I am an avid supporter of vagrant and the [vagrant-libvirt](https://linuxsimba.com/vagrant-libvirt-install) component. Unfortunately, Juniper only officially released the vqfx10k VM for vagrant-virtualbox.

I like vagrant-libvirt for a few reasons. Vagrant-libvirt has the advantage of using KVM tech which has a smaller memory footprint then Virtualbox. Also [QEMU uses very resilient UDP tunnels for point to point connections](https://linuxsimba.com/qemu-tunnel-types) between VMS. This means you can simulate a large network, say 50 switches without having to create 50 Linux bridges and managing all the messiness of bridges.

This blog post goes over how to create a Vagrant libvirt box for Vqfx10k.

## Install Vagrant Libvirt
I have a post on [how to install vagrant-libvirt](https://linuxsimba.com/vagrant-libvirt-install). Also the [official vagrant-libvirt github site](https://github.com/vagrant-libvirt/vagrant-libvirt) has further details.

## Install virtualbox
Install Virtualbox via a Linux system package manager (apt/yum). After creating a vagrant qcow2 formatted Box, you can delete all Virtualbox system packages, if you want.

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

The problem with the Virtualbox vqfx10k is that the ``em0``, the management interface for vqfx10k, is already assigned an IP address of ``10.0.2.15``. If you take this Virtualbox OVF, and convert it to a QCOW2 image, and boot it up, ``em0`` fails to pick up an IP address from the dnsmasq server running on the ``vagrant-libvirt`` Linux bridge created by vagrant-libvirt.

The Vqfx10k VM continously sends out a DHCPREQUEST instead of sending a DHCPDISCOVER. So DNSMasq ignores the request and nothing happens.

```
root@vqfx-re> show dhcp client binding
IP address        Hardware address   Expires     State      Interface
10.0.2.15         00:0f:81:61:36:00  0           REQUESTING em0.0
```

I suspect the Juniper builders of the Virtualbox VM did not take this problem into account because it always works with Virtualbox.


To clear this issue, run the command ``clear  dhcp client binding all`` from the console.

The Vqfx10k Virtualbox VM already has a vagrant user with the insecure Vagrant SSH key, using ``vagrant ssh`` just works.

After running the command to clear the DHCP client bindings, the Vqfx10k VM now has a working DHCP management Interface

```
root@vqfx-re> show dhcp client binding
IP address        Hardware address   Expires     State      Interface
0.0.0.0           00:0f:81:61:36:00  0           INIT       em0.0
```

Packer is used to fix the existing OVF created by Juniper. Packer has the ability to modify an OVF via its console connection and save the changes made to the OVF in a new Vagrant Box.
This is what the ``fix_junos_dhcp.json`` packer config file does. Download it from the Linuxsimba libvirt-network-switches git repo.

```

git clone https://github.com/linuxsimba/libvirt-network-switches
cd libvirt-network-switches
vagrant box add juniper/vqfx10k-re
cp -rv $HOME/.vagrant.d/boxes/juniper-VAGRANTSLASH-vqfx10k-re/0.2.0/virtualbox/* .
packer build fix_junos_dhcp.json

```
After Packer builds a fixed Vagrant Box with an updated Virtualbox OVF, proceed to convert the Box into a vagrant-libvirt compatible box using [vagrant-mutate](https://github.com/sciurus/vagrant-mutate)

```
vagrant plugin install vagrant-mutate
vagrant box add boxes/junos_dhcp_fixed.box --name "vqfx10k-re-fixed-dhcp"
vagrant mutate vqfx10k-re-fixed-dhcp libvirt
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
