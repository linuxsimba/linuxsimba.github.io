---
title: Add A Serial Console to Packer Generated VMs
tags: ['packer','console', 'vagrant']
---

Most of the time I have console access to VMs via [virt-manager](https://virt-manager.org/).

But sometimes I do not have virt-manager access to the hypervisor.
I found it really handy, before creating any new vagrant environment, to add console support to the vagrant boxes.
This means I can use the ``virsh console [domain]``

Here is the scripts for Ubuntu14.04 and Centos7 to add to the packer provisioner script list.

### scripts/ubuntu/console.sh
```
#!/bin/sh -eux

# Add Console Support to the Ubuntu image

ubuntu_version="`lsb_release -r | awk '{print $2}'`";
ubuntu_major_version="`echo $ubuntu_version | awk -F. '{print $1}'`";

# Work around bad cached lists on Ubuntu 12.04
#if [ "$ubuntu_version" = "12.04" ]; then
#    apt-get clean;
#    rm -rf /var/lib/apt/lists;
#fi

cat <<EOF >/etc/init/ttyS0.conf
start on stopped rc RUNLEVEL=[12345]
stop on runlevel [!12345]

respawn
exec /sbin/getty -L 115200 ttyS0 vt102
EOF

current_line='GRUB_CMDLINE_LINUX='
modified_line='GRUB_CMDLINE_LINUX="console=tty0 console=ttyS0, 115200n8"'
sed -i "s/^$current_line/$modified_line/" /etc/default/grub

```
_[Download](https://github.com/linuxsimba/packer-libvirt-profiles/blob/master/scripts/ubuntu/console.sh)_

### scripts/centos/console.sh
```
#!/bin/sh -eux

# Add Console Support to the Centos image`


# add console=ttyS0 to the end of the grub config file
# First check to see if console=ttyS0 is configured first

if grep -q "console=ttyS0" /etc/sysconfig/grub; then
  echo "No Change to the Serial Console setting"
else
  echo "Apply Serial Console setting to the Centos Based VM"
  sed -e  '/GRUB_CMDLINE_LINUX/ s/.$//' -e '/GRUB_CMDLINE_LINUX/ s/$/ console=ttyS0"/' /etc/default/grub > /tmp/grub.tmp

  mv /tmp/grub.tmp /etc/default/grub
  # activate the change
  grub2-mkconfig -o /boot/grub2/grub.cfg
fi

```
_[Download](https://github.com/linuxsimba/packer-libvirt-profiles/blob/master/scripts/centos/console.sh)_

