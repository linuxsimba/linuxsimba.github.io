---
title: Creating Ansible Inventory from Netbox Data
tags: ['netbox', 'ansible']
---

[Netbox](http://github.com/digitalocean/netbox) is a Datacenter Inventory Management
System (DCIM) and IP Address Management System all rolled into one.

Netbox provides a simple API whose documentation can be accessed via the "/api/docs"
url of the Netbox server. I believe it is Swagger 1.2 compatible format.

## Prerequisites

#### Latest Netbox

Currently tested using [git ref 298ac1ba](https://github.com/digitalocean/netbox/commit/298ac1ba7a19ce4dadbd7d6bf857dbb1fc61aaa9)
Basically you should have the patches for [API authentication](https://github.com/digitalocean/netbox/issues/724)

#### Configure 4 shell environment variables

_Example:_

```
export NETBOX_URL=http://localhost
export NETBOX_USER=admin
export NETBOX_PASSWD=admin
export PXE_SERVER=192.168.1.1
```

#### Provide a specific format for the Netbox device roles

This is a way to define multiple roles for a particular device because Netbox does not support adding multiple roles to one device.


**Example 1**: _"linux-switch"_ device role means that the device is placed in the ``[linux]``
 and ``[switch]`` Ansible inventory groups respectively.

**Example 2**: _"windows-authentication"_ device role means that the device is placed in
the ``[windows]`` and ``[authentication]`` Ansible inventory groups respectively.

> NOTE:  Linux Switches inventory entries like Cumulus switches entries will not have an interface list like other linux devices, i.e servers.


## Testing the Ansible Dynamic Inventory Script

Download the [netbox-ansible inventory script](https://gist.github.com/linuxsimba/7726aa6f67ae3cbbd9c61efdf37b8c88). Run this simple ansible playbook and command to test the inventory.

#### test.yml
```
---
- hosts: all
  gather_facts: false
  tasks:
    - debug: var=hostvars[inventory_hostname]
```

```
$ chmod +x netbox-ansible.py
$ ansible-playbook -i netbox-ansible.py test.yml
```

This is a snippet of some sample output

```
      "x1-r1": {
            "hosts": [
                "172.17.100.202"
            ],
            "vars": {
                "interfaces": {
                    "eth0": {
                        "ip": "",
                        "mac": "F3:11:22:33:44:55"
                    },
                    "eth1": {
                        "ip": "",
                        "mac": "F4:33:11:33:22:11"
                    },
                    "ipmi": {
                        "ip": "172.17.200.10/26",
                        "mac": "08:11:33:22:11"
                    }
                },
                "primary_ip_addr": "172.17.100.202",
                "primary_ip_prefix": "26"
            }
        },
        "switch": {
            "children": [
                "leaf1",
                "leaf2",
                "mgmt-switch"
            ]

```
