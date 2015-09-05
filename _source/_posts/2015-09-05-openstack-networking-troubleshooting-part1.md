---
title: Vlan Troubleshooting in a Openstack OVS L2 Agent Environment
tags: ['openstack', 'neutron', 'ovs']
---

Today I am learning OpenVSwitch and using the OpenVswitch in a virtual Openstack
topology.

Got a simple question with a really long explanation.

If someone provides the name of a VM and their tenant (_or project_) name, what
Vlan is the VM assigned to? The solution presented is long..really long.  Will
ask on the #openstack-neutron forum if this solution is correct. Seems very long
and complicated.

#### Log as the openstack admin

```
[root@server1 ~]# source /root/keystonerc_admin
[root@server1 ~(keystone_admin)]#

```

#### Get the project ID

```
[root@server1 ~(keystone_admin)]# openstack project show demo
+-------------+----------------------------------+
| Field       | Value                            |
+-------------+----------------------------------+
| description | default tenant                   |
| enabled     | True                             |
| id          | c6025d15149f4ab3b001e33724837f1c |
| name        | demo                             |
+-------------+----------------------------------+

```

#### Get the ID of the VM in question
With the project ID, get the list of VMs and obtain the ID of the
``demo-instance-202`` VM.

```
[root@server1 ~(keystone_admin)]# nova list --tenant c6025d15149f4ab3b001e33724837f1c
+--------------------------------------+-------------------+----------------------------------+--------+------------+-------------+----------------------+
| ID                                   | Name              | Tenant ID
| Status | Task State | Power State | Networks             |
+--------------------------------------+-------------------+----------------------------------+--------+------------+-------------+----------------------+
| 3a992407-8af7-4af1-b4ea-5945324f58fc | demo-instance-202 | c6025d15149f4ab3b001e33724837f1c | ACTIVE | -          | Running     | demo123=10.100.1.105 |
| 25948f29-a99f-458b-997d-42cb02193148 | demo-instance-203 | c6025d15149f4ab3b001e33724837f1c | ACTIVE | -          | Running     | demo123=10.100.1.106 |
+--------------------------------------+-------------------+----------------------------------+--------+------------+-------------+----------------------+

```

### Get the virsh instance name
With the server ID, get the virsh instance name. From what I have read you can
only do this as a openstack admin. As a tenant user, you do not appear to have
visibility to this infomation

```
[root@server1 ~(keystone_admin)]# nova show 3a992407-8af7-4af1-b4ea-5945324f58fc
+--------------------------------------+----------------------------------------------------------+
| Property                             | Value
|
+--------------------------------------+----------------------------------------------------------+
| OS-DCF:diskConfig                    | MANUAL
|
| OS-EXT-AZ:availability_zone          | nova
|
| OS-EXT-SRV-ATTR:host                 | server1
|
| OS-EXT-SRV-ATTR:hypervisor_hostname  | server1
|
| OS-EXT-SRV-ATTR:instance_name        | instance-00000085
|
| OS-EXT-STS:power_state               | 1
|
| OS-EXT-STS:task_state                | -
|
....
..............
...................

```

### Get the VM tap interface and bridge assigned to it

From the [Openstack OVS L2 Agent
Page](http://docs.openstack.org/developer/neutron/devref/openvswitch_agent.html), the following diagram shows the
patchwork of interfaces used to connect a VM to the outside world.
![blah](http://docs.openstack.org/developer/neutron/_images/under-the-hood-scenario-1-ovs-compute.png)
The following sections will go through this patchwork of interface to see what
the output looks like on a compute node.

First use virsh to get the tap and bridge interface names

```
[root@server1 ~(keystone_admin)]# virsh domiflist instance-00000085
Interface  Type       Source     Model       MAC
-------------------------------------------------------
tap89e91978-38 bridge     qbr89e91978-38 virtio      fa:16:3e:f9:7a:4b


root@server1 ~(keystone_admin)]# brctl show qbr89e91978-38
bridge name       bridge id         STP   interfaces
qbr89e91978-38    8000.1215b1d823f9 no    qvb89e91978-38
                                          tap89e91978-38

```

### Get the OVS port name in the "br-int" bridge.
In the previous output, the bridge is called ``qbr89e91978-38`` so its
associated OVS port name is ``qvo89e91978-38 ``.

### Check the OVS tables for the internal tag associated with the OVS port
The ovs port ``qvo89e91978-38`` is assigned an internal tag. To get the tag
info, run

```
root@server1 ~(keystone_admin)]# ovs-vsctl find Port name="qvo89e91978-38"
_uuid               : 84edc4bb-7c7b-442f-a320-fb4115ac0728
bond_active_slave   : []
bond_downdelay      : 0
bond_fake_iface     : false
bond_mode           : []
bond_updelay        : 0
external_ids        : {}
fake_bridge         : false
interfaces          : [1dd0acb7-f2c4-4774-806d-2341439c6c6f]
lacp                : []
mac                 : []
name                : "qvo89e91978-38"
other_config        : {}
qos                 : []
statistics          : {}
status              : {}
tag                 : 5
trunks              : []
vlan_mode           : []
```

So the tag id is **Five**

### Check the OVS flow table to see what vlan tag id "5" is translated to

According to the ``ovs-ofctl dump-flows br-int`` command, internal tag of 5 is
translated to vlan 161. Phew! that was tough! Why is it this complicated??

<pre>
[root@server1 ~(keystone_admin)]# ovs-ofctl dump-flows br-int
NXST_FLOW reply (xid=0x4):
 cookie=0x0, duration=21985.474s, table=0, n_packets=3163, n_bytes=284347,
idle_age=19, priority=1 actions=NORMAL
 <strong>cookie=0x0, duration=5465.876s, table=0, n_packets=825, n_bytes=83510,
idle_age=19, priority=3,in_port=1,dl_vlan=161
actions=mod_vlan_vid:5,NORMAL</strong>
 cookie=0x0, duration=21984.106s, table=0, n_packets=27, n_bytes=2658,
idle_age=4435, priority=2,in_port=1 actions=drop
 cookie=0x0, duration=21985.293s, table=23, n_packets=0, n_bytes=0,
idle_age=21985, priority=0 actions=drop

</pre>
