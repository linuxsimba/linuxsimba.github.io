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
