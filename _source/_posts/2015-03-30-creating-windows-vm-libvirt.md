---
title: Creating Windows KVM VM using Libvirt
tags: ['windows', 'libvirt']
---

I recently wrote an article for Cumulus Linux about how to setup [Debian Linux
as an Active Directory LDAP Client](http://bit.ly/1xuo8i0).

These are my notes for creating a windows VM in libvirt for the article.

### Prerequisites for Windows VM on Libvirt
* Licensed copy of Windows 2008 server to my hard disk. To make a copy I used

```
dd if=/dev/sr0 of=/home/linuxsimba/isos
```

* [libvirt](https://help.ubuntu.com/lts/serverguide/libvirt.html) and [libguestfs-tools](http://libguestfs.org/). These provide the `qemu-img`,
* `virt-builder`, `virt-install` and `virsh` commands needed to get the windows VM working.
* [virtio storage driver](http://alt.fedoraproject.org/pub/alt/virtio-win/latest/images/bin/). Provides the storage driver for windows 2008 to see the qcow2 virtio disk image. I could have used IDE..but thought it might be interesting to see how to setup virtio disk for Windows.


### Create the Hard disk
Created a 20G Qcow2 hard drive

```
# mkdir $HOME/imgs
# cd $HOME/imgs
# qemu-img create -f qcow2 windows_ad.qcow2 20G
```

### Run virt-builder to create the libvirt domain entry
```
# mkdir $HOME/isos
# virt-install  --name=windows_ad --ram 2048 --disk $HOME/imgs/windows_ad.qcow2,format=qcow2,bus=virtio,cache=none,size=10 --os-type windows --cdrom $HOME/isos/win2008.iso --graphics spice
```

This command causes the Windows VM installation to begin.
But I do not want to start it yet. I need to add the 2nd CDROM,
the virtio driver. So I opened the console using
``virt-viewer windows_ad`` , and shutdown the VM by force.

### Add 2nd CDROM to Windows VM
libvirt doesn't [provide an elegant solution](http://superuser.com/questions/239870/change-cd-rom-via-virsh). So I edited the domain file directly
and added a second CDROM. The disk section of the domain file looked like this when I was done.

```bash
# virsh edit windows_ad

```

```xml
 <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' cache='none'/>
      <source file='/home/linuxsimba/imgs/windows_ad.qcow2'/>
      <target dev='vda' bus='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05'
function='0x0'/>
    </disk>
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <source file='/home/linuxsimba/isos/win2008.iso'/>
      <target dev='hda' bus='ide'/>
      <readonly/>
      <address type='drive' controller='0' bus='0' target='0' unit='0'/>
    </disk>
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <source file='/home/linuxsimba/isos/virtio-win-0.1-94.iso'/>
      <target dev='hdc' bus='ide'/>
      <readonly/>
      <address type='drive' controller='0' bus='1' target='0' unit='0'/>
    </disk>

```

### Proceed with the Windows install

```
# virsh start windows_ad
# virt-viewer windows_ad
```

I performed a Standard Installation x86 Full installation.

###  Load virtIO driver from the 2nd CDROM

To get the 20G disk to show, the virtio driver has to be loaded. Here are
screenshots showing how I did it
![Click on Load Driver](https://lh3.googleusercontent.com/-onau5fRfR1c/VRn_2-4mXCI/AAAAAAAAF8c/p3Kai2irQSc/s0/screenshot_of_load_driver.png
"screenshot_of_load_driver.png")

![Select Win7 AMD64 Driver](https://lh3.googleusercontent.com/--O9vb8uCVt4/VRn_mfsUBSI/AAAAAAAAF8M/S3mElzQEvQM/s0/screenshot_of_libvirtio_install2.png
"screenshot_of_libvirtio_install2.png")
![Select VirtIO driver](https://lh3.googleusercontent.com/-qL5gkHFbtiQ/VRoAHlEY_XI/AAAAAAAAF8w/Rx6IjtDtXmk/s0/screenshot_of_libvirtio_install1.png
"screenshot_of_libvirtio_install1.png")

### Rest of the Installation
The rest of the installation was just like a normal Windows 2008 install.

### Take a Snapshot when the install is done
To ensure I don't have to do this for a while, I shutdown the VM and took a
[snapshot of the image](http://kashyapc.com/2011/10/04/snapshotting-with-libvirt-for-qcow2-images/).
Then proceeded to configure Active Directory with LDAP over SSL support, which I will discuss in a later post.

```bash
# virsh shutdown windows_ad
# virsh snapshot-create windows_ad
# virsh start windows_ad
# virt-viewer windows_ad
```
