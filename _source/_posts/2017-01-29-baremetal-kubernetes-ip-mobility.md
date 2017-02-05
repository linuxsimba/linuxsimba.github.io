---
title: "BareMetal Kubernetes IP Mobility"
tags: ['kubernetes']
---

As of Jan 29 2017, almost all Kubernetes networking documentation assume that the Kubernetes cluster runs in some kind of public or private cloud technology. For example, [Openstack, AWS or GCE](https://kubernetes.io/docs/user-guide/load-balancer/)


What about Baremetal Kubernetes? Currently [Mirantis](https://mirantis.com) seems to be the only company addressing the IP mobility problem in Baremetal Kubernetes.

### What is the Problem?

One can deploy Kubernetes using a tool like [Kargo](https://github.com/kubernetes-incubator/kargo) onto baremetal CoreOS or
Ubuntu hosts. Probably even on [Redhat Atomic](http://www.projectatomic.io/). But the problem is after you go through that work,
how to do you configure IP Mobility for a pod within the cluster?

Kubernetes has the concept of configuring [ExternalIPs](https://kubernetes.io/docs/tutorials/stateless-application/expose-external-ip-address/  ) on the [Service Resources](https://kubernetes.io/docs/user-guide/services/) that you configure like so:

```
kind: Service
apiVersion: v1
metadata:
  name: "frontend"
spec:
  selector:
    app: "frontend"
  ports:
    - protocol: "TCP"
      port: 443
      targetPort: 443
  type: NodePort
  externalIPs:
    - 200.1.1.1
```

In the above example the *frontend* loadbalancer service is created for the *frontend* pod(*app*). The service is assigned 200.1.1.1 as the external facing IP. On baremetal Kubernetes, you the admin,  are responsible for configuring the 200.1.1.1/32 IP address onto the appropriate Kubernete minions and redistributing this route into your network routing tables. *Painful task!*

Kubernetes clusters on top of Openstack, AWS or GCE have a solution for IP Mobility. It calls it [*cloud providers*](https://github.com/kubernetes/kubernetes/tree/master/pkg/cloudprovider/providers).
Example:

```
kind: Service
apiVersion: v1
metadata:
  name: "frontend"
spec:
  selector:
    app: "frontend"
  ports:
    - protocol: "TCP"
      port: 443
      targetPort: 443
  type: LoadBalancer
```
The above configuration triggers the cloud provider code to give the service an externally facing IP. So almost by magic. providing the service with IP mobility.  Watch Kelsey Hightower [demonstrate a service created using a cloud provide loadbalancer](https://www.youtube.com/watch?time_continue=78&v=H8BO3bhnIFQ). Notice in the video the External IP. It appears magically without any user intervention.

I'm not sure if you destroy and restore  the service, if the cloud provider code gives the service the same IP each time..hmmm?

### The IP Mobility Solution for Baremetal Kubernetes

[Mirantis](https://mirantis.com) have developed a *cloud provider* of sorts. It is called the [external IP controller](https://github.com/Mirantisyou /k8s-externalipcontroller).
In a nutshell, its a set of apps that listens to service resource requests, i.e loadbalancer service requests, and adds the ExternalIP address to the interface of choice on the kubernetes minions. Using the example shown earlier, when the External IP controller is installed, it takes the External IP and adds it to an interface on the Kubernetes minion. Which Kubernetes minion does it add it to? The minion running a claimsController pod. The interface is determined by the external IP controller config.

So if you have multiple claimControllers you can place the external IP on multiple kubernetes minions and use ECMP routing instead of configuring a dedicated loadbalancer.


#### Where the claimsController is running

Notice it says the *claimController* is running on k8s6 and k8s9 nodes.

```
$ kubectl get po -l app=externalipcontroller -o wide
NAME                              READY     STATUS              RESTARTS   AGE       IP         NODE
claimcontroller-711596365-1rv9j   1/1       Running             4          1d        10.1.3.6   k8s6
claimcontroller-711596365-b608s   1/1       Running             4          3d        10.1.3.9   k8s9
```

The number of *claimController* pods is managed by the *claimController* deployment

```
$ kubectl get deploy -l app=externalipcontroller
NAME              DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
claimcontroller   2         2         2            2           6d
```

#### Where is the External IP placed?

Let's review all the Kubernetes nodes in the cluster and examine their L3 config. The tool used to view L3 config is called [netshow](https://pypi.python.org/pypi/netshow-linux-lib/1.1.5), a Cumulus Network app.

> Notice that where the *claimsController* pod runs, the `200.1.1.1` address is assigned  to that interface.


<pre>
<code>
$ ansible -m command -a 'netshow l3' all

<strong>k8s9</strong> | SUCCESS | rc=0 >>

--------------------------------------------------------------------
    Name    Speed      MTU  Mode          Summary
--  ------  -------  -----  ------------  ---------------------------------------------------
UP  eth0    -1M       1500  Interface/L3  IP: 192.168.200.28/24(DHCP)
UP  lo      N/A      65536  Loopback      IP: 127.0.0.1/8, 10.1.3.9/32, <strong>200.1.1.1/32</strong>, ::1/128

k8s1 | SUCCESS | rc=0 >>

--------------------------------------------------------------------
    Name     Speed      MTU  Mode          Summary
--  -------  -------  -----  ------------  -------------------------------------
UP  eth0     -1M       1500  Interface/L3  IP: 192.168.200.20/24(DHCP)
UP  lo       N/A      65536  Loopback      IP: 127.0.0.1/8, 10.1.3.1/32, ::1/128
UP  vagrant  -1M       1500  Interface/L3  IP: 192.168.121.198/24

<strong>k8s6</strong> | SUCCESS | rc=0 >>

--------------------------------------------------------------------
    Name    Speed      MTU  Mode          Summary
--  ------  -------  -----  ------------  ---------------------------------------------------
UP  eth0    -1M       1500  Interface/L3  IP: 192.168.200.25/24(DHCP)
UP  lo      N/A      65536  Loopback      IP: 127.0.0.1/8, 10.1.3.6/32, <strong>200.1.1.1/32</strong>, ::1/128

k8s4 | SUCCESS | rc=0 >>

--------------------------------------------------------------------
    Name    Speed      MTU  Mode          Summary
--  ------  -------  -----  ------------  -------------------------------------
UP  eth0    -1M       1500  Interface/L3  IP: 192.168.200.23/24(DHCP)
UP  lo      N/A      65536  Loopback      IP: 127.0.0.1/8, 10.1.3.4/32, ::1/128

k8s3 | SUCCESS | rc=0 >>

--------------------------------------------------------------------
    Name    Speed      MTU  Mode          Summary
--  ------  -------  -----  ------------  -------------------------------------
UP  eth0    -1M       1500  Interface/L3  IP: 192.168.200.22/24(DHCP)
UP  lo      N/A      65536  Loopback      IP: 127.0.0.1/8, 10.1.3.3/32, ::1/128

k8s10 | SUCCESS | rc=0 >>

--------------------------------------------------------------------
    Name    Speed      MTU  Mode          Summary
--  ------  -------  -----  ------------  --------------------------------------
UP  eth0    -1M       1500  Interface/L3  IP: 192.168.200.29/24(DHCP)
UP  lo      N/A      65536  Loopback      IP: 127.0.0.1/8, 10.1.3.10/32, ::1/128

k8s11 | SUCCESS | rc=0 >>

--------------------------------------------------------------------
    Name    Speed      MTU  Mode          Summary
--  ------  -------  -----  ------------  --------------------------------------
UP  eth0    -1M       1500  Interface/L3  IP: 192.168.200.30/24(DHCP)
UP  lo      N/A      65536  Loopback      IP: 127.0.0.1/8, 10.1.3.11/32, ::1/128

k8s5 | SUCCESS | rc=0 >>

--------------------------------------------------------------------
    Name    Speed      MTU  Mode          Summary
--  ------  -------  -----  ------------  -------------------------------------
UP  eth0    -1M       1500  Interface/L3  IP: 192.168.200.24/24(DHCP)
UP  lo      N/A      65536  Loopback      IP: 127.0.0.1/8, 10.1.3.5/32, ::1/128

k8s2 | SUCCESS | rc=0 >>

--------------------------------------------------------------------
    Name    Speed      MTU  Mode          Summary
--  ------  -------  -----  ------------  -------------------------------------
UP  eth0    -1M       1500  Interface/L3  IP: 192.168.200.21/24(DHCP)
UP  lo      N/A      65536  Loopback      IP: 127.0.0.1/8, 10.1.3.2/32, ::1/128

k8s8 | SUCCESS | rc=0 >>

--------------------------------------------------------------------
    Name    Speed      MTU  Mode          Summary
--  ------  -------  -----  ------------  -------------------------------------
UP  eth0    -1M       1500  Interface/L3  IP: 192.168.200.27/24(DHCP)
UP  lo      N/A      65536  Loopback      IP: 127.0.0.1/8, 10.1.3.8/32, ::1/128
</code>
</pre>



The External IP Controller can use any subnet mask you tell it and using IpPool definition files, those yaml files
that `kubectl create` accepts, you can vary the subnet mask based on the External IP selected.

The external IP controller can also auto-allocate the IP, just like the cloud provider code does.
But after some time using it, it seems better to  preset the IP using the ExternalIP keyword
in the Services definition file.


#### Enabling IP External controller

There are [instructions on the github page](https://asciinema.org/a/95449) on how to configure it manually. It was easier through
to just include the [kargo-compatible external IP controller role](https://github.com/openstack/fuel-ccp-installer/tree/master/utils/kargo/roles/externalip) in the Kargo ansible playbook, then add this diff to the playbook. Then run ``ansible-playbook cluster.yml -t externalip`` to install the feature on the Kubernetes cluster.

```patch
iff --git a/inventory/group_vars/all.yml b/inventory/group_vars/all.yml
index d87d687..ec2a07f 100644
--- a/inventory/group_vars/all.yml
+++ b/inventory/group_vars/all.yml
@@ -1,3 +1,22 @@
+# External IP controller settings
+
+# Use the latest external ip controller code
+extip_image_tag: "latest"
+
+# Only create /32 entries
+extip_mask: 32
+
+# attach the created IPs to the lo interface
+extip_iface: lo
+
+# For ECMP place the generated IPs on 2 kubernetes minions
+extip_ctrl_replicas: 2
+
+# Apply IP on all claimcontrollers..use network ECMP
+extip_distribution: all
+
```


```patch
diff --git a/cluster.yml b/cluster.yml
index becad3b..d9225ea 100644
--- a/cluster.yml
+++ b/cluster.yml
@@ -26,7 +26,7 @@
 - hosts: k8s-cluster:etcd:calico-rr
   any_errors_fatal: true
   roles:
-    - { role: kubernetes/preinstall, tags: preinstall }
+    - { role: kubernetes/preinstall, tags: ['preinstall','externalip'] }
     - { role: docker, tags: docker }
     - { role: rkt, tags: rkt, when: "'rkt' in [ etcd_deployment_type, kubelet_deployment_type ]" }

@@ -58,6 +58,7 @@
   roles:
     - { role: dnsmasq, when: "dns_mode == 'dnsmasq_kubedns'", tags: dnsmasq }
     - { role: kubernetes/preinstall, when: "dns_mode != 'none' and resolvconf_mode == 'host_resolvconf'", tags: resolvconf }
+    - { role: externalip , tags: 'externalip' }

```
