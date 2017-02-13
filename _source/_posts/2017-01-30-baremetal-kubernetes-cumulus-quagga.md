---
title: "BareMetal Kubernetes Cumulus Quagga Integration"
tags: ['kubernetes','quagga']
---

Kubernetes is a framework that is well suited for completely Layer3 environments.
This article describes how to integrate [Cumulus Router on a Host](https://cumulusnetworks.com/routing-on-the-host/) and [Cumulus BGP Unnumbered](https://docs.cumulusnetworks.com/display/DOCS/Border+Gateway+Protocol+-+BGP#BorderGatewayProtocol-BGP-unnumberedUsingBGPUnnumberedInterfaces) technology
with BareMetal Kubernetes.

### BGP Unnumbered L3 CLOS

For the first part of the integration, create a BGP Unnumbered L3 CLOS.
![L3 Topology ](https://lh3.googleusercontent.com/-6NUEFJABlyY/WJmcyyzBXhI/AAAAAAAANj4/hyCGCCWlb5w4_DG5MXjgH5SCgIUrVdZlgCLcB/s0/cumulus-kubernetes.png "cumulus-kubernetes.png")


The advantages of using BGP Unnumbered are:
<table>
<tr>
<td>
Easier IP Management </td><td>BGP Unnumbered significantly reduces the number of IPs to manage in the underlay. In general one IP is required per leaf and spine node.
Border leafs are the only switches with more than one IP static IP</td></tr>
<tr><td>
Using 4byte BGP Autonomous system numbers (ASNs) together with External BGP peering
</td><td>
 Each device in the L3 topology gets its own
BGP ASN. This makes troubleshooting server or container location  easier. Also data path troubleshooting is simplified by
just reviewing the ASN path to a prefix that matches a Kubernetes container
</td>
</tr>
</table>
Cumulus Networks provide  [more details about BGP unnumbered]().

There are a few ways to configure the switches. Ansible config management was used and not [Cumulus's NCLU](https://docs.cumulusnetworks.com/display/DOCS/Network+Command+Line+Utility).  Use what you prefer, CLI or config management tools.


A [Vagrant simulation](https://github.com/linuxsimba/kubernetes-cumulus-l3-clos) is available.

 More generic examples can be found on the [Cumulus's website](https://github.com/CumulusNetworks/cldemo-roh-ansible) as well.

### Router to the Host

The next part of the integration is to use Cumulus's Router on a Host technology to extend BGP Unnumbered down to the host.

The hypervisor used in this example is Ubuntu 16.04.

> Hope to redo this part of the blog using CoreOS instead. Currently learning CoreOS.


#### Deploy the Quagga Container to the hosts
Used the [instructions available on Cumulus Networks's website](https://docs.cumulusnetworks.com/display/ROH/Installing+the+Cumulus+Quagga+Package+on+a+Host+Server) on how to deploy a Quagga container. The key thing is that the docker container runs in [privileged mode](https://docs.docker.com/engine/reference/run/#/runtime-privilege-and-linux-capabilities).

Configure your Kubernetes nodes to be singly attached. The assumption is that application high availability is handled by Kubernetes. No more use of layer2 MLAG Bonds !


Then for the interface configuration, assign the ``lo`` interface with a /32 address. In Ubuntu 16.04 using [ifupdown2]() the config looks like this:


```
auto lo
iface lo inet loopback
  address 10.1.3.1/32

auto eth1
iface eth1
   description ipv6 link local connection to the leaf switch  
```

Then provision a Quagga.conf with BGP unnumbered config just like a Cumulus leaf or switch, with some redistribute connected and redistributed kernel statements.


```
interface  eth1
  no ipv6 nd suppress-ra
  ipv6 nd ra-interval 3
!
router bgp 65801
  no bgp default ipv4-unicast
  bgp bestpath compare-routerid
  bgp default show-hostname
  bgp router-id 10.1.3.1
  maximum-paths 64
  bgp bestpath as-path multipath-relax
  neighbor fabric peer-group
  neighbor fabric description Internal Fabric network
  neighbor fabric advertisement-interval 0
  neighbor fabric timers 1 3
  neighbor fabric timers connect 3
  neighbor fabric remote-as external
  neighbor fabric capability extended-nexthop
  neighbor eth1 interface peer-group fabric

  address-family ipv4 unicast
     redistribute connected route-map LOOPBACK
     redistribute kernel route-map K8SROUTES
     neighbor fabric activate
  exit-address-family
!
access-list LOOPBACK permit 10.1.3.0/24
access-list K8SROUTES permit 10.233.64.0/18
!
route-map LOOPBACK permit 10
  match ip address LOOPBACK
!
route-map K8SROUTES permit 10
  match ip address K8SROUTES

```

`10.233.64.0/18` is the IP address pool used for Kubernete pod assignments. Each Kubernetes pod gets one IP address.
`10.1.3.0/24` is the IP range assigned to hosts using BGP unnumberered.

This template configuration can be applied to all Kubernetes nodes.

A [Vagrant simulation](https://github.com/linuxsimba/kubernetes-cumulus-l3-clos) is available.


#### Finally Configure Kubernetes node to use the /32 address provisioned.

Assign the ``hypercube kubelet`` container IP address to the /32 used by BGP unnumberered.
Example:

<pre><code>
$ ps -ef | grep kubelet

/hyperkube kubelet --v=2 --address=10.1.3.1 --hostname-override=k8s1 --allow-privileged=true --pod-manifest-path=/etc/kubernetes/manifests --pod-infra-container-image=gcr.io/google_containers/pause-amd64:3.0 --cluster_dns=10.233.0.2 --cluster_domain=cluster.local --resolv-conf=/etc/resolv.conf --kubeconfig=/etc/kubernetes/node-kubeconfig.yaml --require-kubeconfig --register-schedulable=false --network-plugin=cni --network-plugin-dir=/etc/cni/net.d

</code></pre>

And finally, review the kubectl data after Kubernetes is installed.
The IP address used by a Kubernetes node to talk to another Kubernetes node is found in the ``hostname`` label. In this case the hostname is a name not an IP. So the node, uses ``/etc/hosts`` to resolve the host name to an IP address.

``/etc/hosts`` was programmed by [Kargo](https://github.com/kubernetes-incubator/kargo), the Kubernetes deployer.

```
# kubectl get node --show-labels                                                    
NAME      STATUS                     AGE       LABELS
k8s1      Ready,SchedulingDisabled   3d        beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s1
k8s2      Ready                      3d        app=ccp-registry,beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s2
k8s3      Ready                      3d        beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s3
                                                                         # cat /etc/hosts      
127.0.0.1	k8s1	k8s1
127.0.0.1 localhost localhost.localdomain
127.0.1.1	vagrant
::1 localhost6 localhost6.localdomain
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
# Ansible inventory hosts BEGIN
10.1.3.2 k8s2 k8s2.cluster.local
10.1.3.3 k8s3 k8s3.cluster.local
10.1.3.1 k8s1 k8s1.cluster.local
# Ansible inventory hosts END

```


## Installation

A [Vagrant Simulation](https://github.com/linuxsimba/kubernetes-cumulus-l3-clos) is available. It provides both Virtualbox and libvirt support.

## Test out a Kubernetes App on the setup

Use [Kelsey Hightowers demo](https://github.com/kelseyhightower/craft-kubernetes-workshop) to create a simple web service. Videos are available on [Udacity Lesson 615 - Section Kubernetes]()
