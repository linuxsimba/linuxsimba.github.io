---
title: "Troubleshooting Mirantis Fuel: Unable to Install OpenStack on Controller"
tags: ['mirantis', 'openstack', 'fuel', 'troubleshooting', 'vagrant']
---

The virtual design setup for installing Mirantis OpenStack in a
vagrant-libvirt environment does not work with the default settings of
Mirantis Fuel. Bad design? Maybe. This series of posts may be changed in the
near future as Mirantis Openstack adventures continue.

<img src='/mirantis-openstack.svg'/>

When deploying OpenStack using Mirantis Fuel in the above setup, it failed with
the following error

{% gist df2cd86bff3802cf28a1 %}

This cryptic error message pointed to the fact the `connectivity_test.pp``
puppet script on node1 failed. Let us see why.


```
$ vagrant ssh fuel_master
$ sudo su -
$ ssh root@node1
$ cd /etc/puppet/modules/osnailyfacter/modular/netconfig
$ puppet apply connectivit_tests.pp

Notice: Scope(Class[main]): MODULAR: connectivity_tests.pp
Checking http://archive.ubuntu.com/ubuntu/
Error: ERROR: Unable to fetch url 'http://archive.ubuntu.com/ubuntu/', error
'Network is unreachable - connect(2)'. Please verify node connectivity to this
URL, or remove it from the settings page if it is invalid. on node
node-1.domain.tld
Error: ERROR: Unable to fetch url 'http://archive.ubuntu.com/ubuntu/', error
'Network is unreachable - connect(2)'. Please verify node connectivity to this
URL, or remove it from the settings page if it is invalid. on node
node-1.domain.tld
```

The node is unable to reach the main Ubuntu repo. What was confusing is that
the OS was installed using the Fuel Master Node. That is via the Admin/PXE
interface (eth0). The Openstack install occurs over the **public** or eth1
interface in this case. Found this a little odd. Why not configure the whole
setup via the admin interface.

Below is the output from the openstack node showing its default route and bridge
setup. It is clearly trying to go out eth1 to get to the internet. Plus, and
this is not shown, the apt sources.list files point to the Ubuntu archives and
not the Fuel master node.

```
root@node-1# route -n
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         172.16.0.1      0.0.0.0         UG    0      0        0 br-ex
10.20.0.0       0.0.0.0         255.255.255.0   U     0      0        0
br-fw-admin
169.254.169.254 -               255.255.255.255 !H    0      -        0 -
172.16.0.0      0.0.0.0         255.255.255.0   U     0      0        0 br-ex
192.168.0.0     0.0.0.0         255.255.255.0   U     0      0        0 br-mgmt
192.168.1.0     0.0.0.0         255.255.255.0   U     0      0        0
br-storage
root@node-1:# brctl show
bridge name bridge id   STP enabled interfaces
br-ex   8000.064a9f1e0d8f no    eth1
              p_408821a5-0
              p_ff798dba-0
br-fw-admin   8000.361122334411 no    eth0
br-mgmt   8000.525400d6b687 no    eth1.101
br-storage    8000.525400d6b687 no    eth1.102
```

Mirantis Fuel has APT mirror support. So the next step was to turn to this on and
see if all installation (OS + OpenStack) will occur over the "Admin" or "PXE boot" interface.

This was done using the command ``fuel-createmirror``. Some trouble was
experienced when this command was first run.  It is documented in [Part 2 of Mirantis Fuel
Troubleshooting]({% post_url 2016-02-08-troubleshooting-mirantis-fuel-7-part2 %})


> Found out later that clicking the "Log" button next to a Node in the "Nodes"
> Tab gives you the puppet log that points to the root cause.
> <img src='/images/view_server_logs.png'/>

