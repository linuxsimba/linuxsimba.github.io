---
title: "Using Pyang to study the OpenConfig Data Model"
tags: ['ansible', "network", "automation"]
---

[Pyang](https://github.com/mbj4668/pyang/wiki/Tutorial) is a tool that helps  convert, difficult to read, [YANG](http://www.yang-central.org/twiki/bin/view/Main/WebHome) files into readable navigationable web pages and YAML


Network Automation is new hot area in the config management world. When studying network automation, it become clear that deciding on a _data model_ was important. The good people of [OpenConfig](http://openconfig.net/) have spent
some time  developing a data model that can applied to different switch and router vendors. OpenConfig defines its networking data model using YANG.
Unfortunately Ansible cannot use this as a data model language so it needs to be converted to YAML.

Pyang, out of the box, does not provide YANG -> YAML conversion. There is a [Pyang Pull Request](https://github.com/mbj4668/pyang/pull/307) that provides YAML support.  Include this file in a git cloned version of PYang before installing Pyang

```
git clone https://github.com/mbj4668/pyang/
cd pyang
wget -O pyang/plugins/yaml.py https://raw.githubusercontent.com/vkosuri/pyang/b2499bc3557142ba6ff26cfa429e59e2dc3351ed/pyang/plugins/yaml.py
python setup.py bdist_wheel
pip install dist/*
```

Let's take a look at how to convert OpenConfig YANG files into navigationable Web pages (_jstree_) and YAML.

## Download OpenConfig YANG files

```
git clone https://github.com/openconfig/public openconfig
cd openconfig
```
## Run Pyang on files that end with "uses ...."

If you try to run pyang on a file that ends with ``uses ....`` like ``uses bgp-top``, then Pyang does print anything.


```
pyang -f tree -p release/models release/models/bgp/openconfig-bgp.yang
module: openconfig-bgp
   +--rw bgp
      +--rw global
      |  +--rw config
      |  |  +--rw as           oc-inet:as-number
      |  |  +--rw router-id?   oc-yang:dotted-quad
      |  +--ro state
      ....
      .......
```
This produces a datamodel in a tree structure. But if you run ``pyang -p release/models -f tree release/models/ospf/openconfig-ospfv2.yang`` you get no output. The ospfv2.yang file does not have a ``uses ...`` at the end of it. The ``openconfig-bgp.yang`` does and is shown below.

```
module openconfig-bgp {
  grouping bgp-top{
    ...
    .....
    ........
  }

uses bgp-top;

}
```

## List augment files after the main YANG file in the pyang argument string

If you review the following output from ``openconfig-interfaces.yang``

```
pyang -f tree -p release/models ./release/models/interfaces/openconfig-interfaces.yang

```
It prints out a tree with only basic interface related info. This info does not include any IP address structures in the data model. If you want to include ip addressing in the data model output then use what is called a [YANG augment](https://github.com/mbj4668/pyang/wiki/Augment). Augment files are added at the end of the main YANG file.

So the example would now be

```
pyang -f yaml -p release/models ./release/models/interfaces/openconfig-interfaces.yang ./release/models/interfaces/openconfig-if-ip.yang
```

An Augment YANG file contains sections that start with the word ``augment``. Example:

```
augment "/oc-if:interfaces/oc-if:interface/oc-if:subinterfaces/" +
   "oc-if:subinterface/oc-ip:ipv6" {
     description
       "Adds address autoconfiguration to the base IP model";

     uses ipv6-autoconf-top;
   }
```

## Use Jstree format to study the datamodel

The Pyang jstree format prints out the YANG model in a easy to read dropdown enabled
web page. This definitely decreases the time it takes to understand how the YANG model is structured

![jstree example](https://lh3.googleusercontent.com/-RXslQfcalsM/Wd5D4CefMhI/AAAAAAAAPO8/paES1v-YobgUcPqwyOUa1fk4Vj5t86oqwCLcBGAs/s0/jstree_output.png "jstree_output.png")

## Converting YANG into YAML for Ansible consumption

Use the PYang YAML format option to convert a YANG model into YAML

```
pyang -f yaml -p release/models ./release/models/interfaces/openconfig-interfaces.yang ./release/models/interfaces/openconfig-if-ip.yang

---
openconfig-interfaces:
  interfaces:
    interface:
      - name:
        config:
          name:
          type:
          mtu:
          description:
          enabled:
          tpid:
    ...
    .....
    ......
```
