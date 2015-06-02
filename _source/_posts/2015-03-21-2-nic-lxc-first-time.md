---
title: Configure LXC with 2 NICs
tags: ['lxc', 'ansible']
---

This is my first dive into LXC. I needed to configure a LXC and apply ansible on
it. Here was my problem definition

* Configure a basic unprivileged LXC instance
* Install an authorized key in the root user directory so I perform passwordless
ssh
* Run an ansible playbook against LXC instance.

I started off by looking at some reference sites:

* [Ubuntu LXC Server Guide](http://help.ubuntu.com/lts/serverguide/lxc.html)
* [How to create multiple network interfaces in an LXC container]
(http://www.boxtricks.com/multiple-network-interfaces-lxc-container)

These are the steps I came with. Not sure if [lxc role 880 from ansible
galaxy](https://galaxy.ansible.com/list#/roles/880) runs what I want. I will
play with the ansible galaxy role and update this post.


#### Install LXC
Not 100% clear to me why rebooting helps. I will update this post when I
figure it out.

```
$ sudo apt-get install lxc
$ sudo reboot
```

#### Setup configuration files

* Configure `$HOME/.config/lxc/default.conf`. Got this info mainly from the [Ubuntu LXC
Server Guide](http://help.ubuntu.com/lts/serverguide/lxc.html)

```
# $HOME/.config/lxc/default.conf
# ------------------------------

lxc.id_map = u 0 100000 65536
lxc.id_map = g 0 100000 65536

lxc.network.type = veth
lxc.network.link = lxcbr0
lxc.network.name = eth0
lxc.network.flags = up

lxc.network.type = veth
lxc.network.flags = up
lxc.network.link = lxcbr1
lxc.network.name = eth1


```

* Configure `/etc/lxc/lxc-usernet`. Add the bridges I(_as the user_) attach my lxc veth
interfaces to.

```
# /etc/lxc/lxc-usernet
# --------------------
USERNAME TYPE BRIDGE COUNT
stanley veth lxcbr0 2
stanley veth lxcbr1 2

```

* Create bridges if missing. I notice that `lxcbr0` is there,  when lxc is
activated and device is reloaded. But not sure how other bridges get initialized
at boot-time. When I figure this out, I will update this post. *For now I
create the missing bridge non-persistently*

```
$ sudo brctl show
bridge name bridge id   STP enabled interfaces
lxcbr0    8000.fe195e4f51ff no

$ sudo brctl addbr lxcbr1

```

* Create path to lxc install directory under my directory and set the
execute bit only for all directories in the path

```
$ mkdir $HOME/.local/share/lxc
$ chmod +x $HOME
$ chmod +x $HOME/.local
$ chmod +x $HOME/.local/share/
$ chmod +x $HOME/.local/share/lxc

```

#### Install LXC instance

Instance is a Ubuntu 14.04 image.

```
$ lxc-create -t download -n u1 -- -d ubuntu -r trusty -a amd64
```

#### Copy User SSH Public Key to LXC instance

```
$ export LXC_HOME=$HOME/.local/share/lxc/u1/rootfs
$ sudo mkdir $LXC_HOME/root/.ssh

$ sudo cp $HOME/.ssh/id_rsa.pub $LXC_HOME/root/.ssh/authorized_keys
$ sudo chown -R 10000:10000 $LXC_HOME/root/
```

#### Start LXC
```
$ lxc-start -n u1 -d
```

### Get LXC IP

```
$ lxc-ls --fancy
NAME  STATE    IPV4        IPV6  AUTOSTART
------------------------------------------
u1    RUNNING  10.0.3.236  -     NO
```

### install SSH on LXC

```
lxc-attach -n u1 -- apt-get update
lxc-attach -n u1 -- apt-get install openssh-server -y
```

### Test SSH Using Ansible

```
$ ansible -m ping all
10.0.3.236 | success >> {
    "changed": false,
    "ping": "pong"
}

```

### confirm two interfaces were configured on LXC

```
$ lxc-attach -n u1 -- ip link show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT
group default
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
10: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP
mode DEFAULT group default qlen 1000
    link/ether ba:61:b6:87:ad:ae brd ff:ff:ff:ff:ff:ff
12: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP
mode DEFAULT group default qlen 1000
    link/ether 26:8d:9a:4c:3f:66 brd ff:ff:ff:ff:ff:ff

$ brctl show
bridge name bridge id   STP enabled interfaces
lxcbr0    8000.fe195e4f51ff no    veth1E270R
              vethSPECOS
lxcbr1    8000.fedc7b73ae49 no    vethX4YOOR

```

### To setup a static IP for the LXC

First modify the ``/etc/default/lxc-net``. Uncomment the following line
``LXC_DHCP_CONFILE`` line.

```
# Uncomment the next line if you'd like to use a conf-file for the lxcbr0
# dnsmasq.  For instance, you can use 'dhcp-host=mail1,10.0.3.100' to have
# container 'mail1' always get ip address 10.0.3.100.
LXC_DHCP_CONFILE=/etc/lxc/dnsmasq.conf
```

Then create the file ``/etc/lxc/dnsmasq.conf`` and add the line

```
dhcp-host=u1, 10.0.3.10
```

Then in my ``/etc/hosts`` I added

```
u1  10.0.3.10
```

## ON MY TODO LIST

My next steps are you look into
[vagrant-lxc](https://github.com/fgrehm/vagrant-lxc) and
[libvirt-lxc](https://libvirt.org/drvlxc.html) providers,
as I am a frequent user of both [Vagrant](http://www.vagrantup.com) and
[Libvirt](http://libvirt.org)

