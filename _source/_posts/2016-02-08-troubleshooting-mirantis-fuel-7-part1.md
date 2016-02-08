---
title: "Troubleshooting Mirantis Fuel: Unable to Install OpenStack on Controller"
tags: ['mirantis', 'openstack', 'fuel', 'troubleshooting', 'vagrant']
---

The virtual design setup for installing Mirantis OpenStack in a
vagrant-libvirt environment doesn not work with the default settings of
Mirantis Fuel.

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

The node is unable to reach the main Ubuntu repo. Decided to read the docs and
not be smarty pants. In Mirantis Fuel default setup, the Openstack node tries to
reach the internet to download what it needs. To do this, the node uses its
**public** interface. So what is the public interface and what is the default
route? Let us see!

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

Well its not ``eth0`` which connects to the fuel master! And remember in the
diagram, I connect ``eth1`` as a back to back link between the 2 nodes.

So decided to see if wiping clean the openstack nodes, and installing an APT
mirror on the Fuel master node using the command ``fuel-createmirror`` will
help. The troubles are faced there are documented in [Part 2 of Mirantis Fuel
Troubleshooting]({% post_url 2016-02-08-troubleshooting-mirantis-fuel-7-part2 %})

