---
title: Linux Sysadmin Rosetta Stone
tags: ['debian', 'redhat']
---

Compares common sysadmin actions between Debian based and RedHat based systems.

> Work in Progress

### Installing Development Tools

<table>
<thead>
<tr>
<td>
<strong>Debian</strong>
</td>
<td>
<strong>RedHat</strong>
</td>
</tr>
</thead>
<tbody>
<tr>
<td>
<pre> apt-get build-essential</pre>
</td>
<td>
<pre>yum groupinstall 'Development Tools'</pre>
</td>
</tr>
</tbody>
</table>


### Configuring a Static IP

<table>
<thead>
<tr><td><strong>Debian</strong> </td><td><strong> Redhat</strong></td></tr>
</thead>
<tbody>
<tr>
<td>
<i>/etc/network/interfaces</i>
<pre>
auto eth1
iface eth1 inet static
   address 10.1.1.1/25
</pre>
</td>
<td>
 <i>/etc/sysconfig/network-scripts/ifcfg-eth1</i>
<pre>
DEVICE=eth1
NAME=eth1
BOOTPROTO=none
ONBOOT=yes
PREFIX=25
IPADDR=10.1.1.1
USERCTL=no
NM_CONTROLLED=no
</pre>
</td>
</tr>
</tbody>
</table>

### Configure a Trunk. Assign a trunk subinterface with a static IP

Ensure that the `802.1q` kernel module is loaded.
<table>
<thead>
<tr><td><strong>Debian</strong> </td><td><strong> Redhat</strong></td></tr>
</thead>
<tbody>
<tr>
<td>
<i>/etc/network/interfaces</i>
<pre>
auto eth1
iface eth1 inet manual
   up ip link set $IFACE up
   down ip link set $IFACE down

auto eth1.10
iface eth1.10 inet static
  address 10.1.1.1/25
</pre>
</td>
<td>
 <i>/etc/sysconfig/network-scripts/ifcfg-eth1</i>
<pre>
DEVICE=eth1
NAME=eth1
BOOTPROTO=none
ONBOOT=yes
USERCTL=no
NM&#95;CONTROLLED=no
VLAN=yes
</pre>
 <i>/etc/sysconfig/network-scripts/ifcfg-eth1.10</i>
<pre>
DEVICE=eth1.10
NAME=eth1.10
BOOTPROTO=none
ONBOOT=yes
PREFIX=25
IPADDR=10.1.1.1
USERCTL=no
NM&#95;CONTROLLED=no
VLAN=yes
</pre>

</td>
</tr>
</tbody>
</table>


### Find a Package associated with a particular file

<table>
<thead>
<tr><td><strong>Debian</strong> </td><td><strong> Redhat</strong></td></tr>
</thead>
<tbody>
<tr>
<td>
<pre>
$ dpkg -S /usr/bin/nice
coreutils: /usr/bin/nice
</pre>
</td>
<td>
<pre>
$ rpm -qf /usr/bin/nice
coreutils-8.22-12.el7_1.2.x86_64
</pre>
</td></tr>
</tbody>
</table>
