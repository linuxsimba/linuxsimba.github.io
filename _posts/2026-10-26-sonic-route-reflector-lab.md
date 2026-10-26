---
title: "Route Reflectors in an AI Scale-Out Network - Learning SONiC/BMP/pytest"
tags: ["ai", "networking", "sonic", "bgp", "containerlab", "pytest"]
---

This morning I watched Alibaba's [OCP talk about decoupling route distribution in AI clusters](https://youtu.be/8in3TD9vW6g?si=AcsvtYCF2_cUPzbs) and thought it sounded interesting.

Microsoft hides GPU IP prefixes from the fabric [with SRv6](https://youtu.be/i6bV9yyybm4?si=ZGRoGENOQeiGl_aG), but Alibaba didn't want to customize their server NICs. So they put route reflectors in their cluster.


## The Setup

As a way to learn SONiC and pytest, I used this scenario as an excuse to build a simulation.

[sonic-rr on GitHub](https://github.com/linuxsimba/sonic-rr)

![topology](https://github.com/linuxsimba/sonic-rr/raw/master/topology.svg)

The goals were as follows:

* The GPU IP prefixes were sent to the route reflectors so all leaves had all the information from the other leaves. A Tomahawk 5 switch like the [Nexthop NH-4020](https://nexthop.ai/downloads/hardware/2605/NH-4020-Product-Datasheet-D010.pdf) lists 850K IPv4 host/LPM routes (128K for IPv6), so each leaf should comfortably hold routes from a whole AI cluster without any summarization, at least for IPv4. I read that there is a knob called `ipv6_lpm_128b_enable` in the Broadcom SDK that allows you to expand the room for IPv6 prefixes in the shared IPv4/IPv6 prefix hardware route table. I could not find any detailed info about it. I guess summarizing IPv6 at the leaf switch may make sense if your cluster is huge? I still need to find some research about scale-out network addressing and what the best practice is.

* Spines can learn GPU IP prefixes but don't send them to the leaves. So instead of leaves getting N(spines) * (number of GPU IPs) BGP updates, with the Alibaba solution the spines only send loopback routes to the leaves. In the tests, with 10k simulated GPU IP routes, pytest showed that with the RR in place, what Alibaba calls the pivot solution, only 4 routes (all loopbacks) were sent to the leaf when a spine failed and recovered. Without an RR, the spine re-sent 10,016 routes to the leaf, every GPU prefix plus the loopbacks.



## Testing With pytest and BMP

I wanted to learn pytest, and I avoided vtysh. I used BMP instead. I wanted gRPC, but that's only in the SONiC VM, not the stripped-down containerlab image, and I don't have the disk space for 8 SONiC VMs.

The results were as expected.

## Results


```
server1 │ dir ~/git/sonic-rr │ git pytest-bgp-recovery ✗ uncommitted
➜ pytest 
==================================================================================== test session starts =====================================================================================
collected 4 items                                                                                                                                                                            

tests/test_bgp_paths.py::test_route_count[traditional] 
--------------------------------------------------------------------------------------- live log setup ---------------------------------------------------------------------------------------
17:17:23 ansible-playbook configure.yml mode=traditional
17:17:23   PLAY [Build inventory from the lab counts]
17:17:23   TASK [Spines]
17:17:23   TASK [Leaves]
17:17:23   TASK [Route servers]
17:17:23   TASK [GPU servers]
17:17:23   PLAY [Wait for the SONiC switches and start the daemons sonic-vs leaves off]
17:17:23   TASK [Wait until orchagent, FRR and all 32 ports are up]
17:17:24   TASK [Restart lldpd (sonic-vs starts it without its control socket)]
17:17:27 BMP session from 172.20.20.14
17:17:28   TASK [Start bfdd (shipped but not started in sonic-vs)]
17:17:28   PLAY [Configure spines]
17:17:28   TASK [Loopback, and one unnumbered port per leaf (Ethernet0 = leaf1, Ethernet4 = leaf2, ...)]
17:17:32   TASK [Render and apply FRR config]
17:17:33   TASK [ansible.builtin.command]
17:17:33   PLAY [Configure leaves]
17:17:33   TASK [Load FRR's BMP module into bgpd on the leaves listed in bmp_leaves]
17:17:34   TASK [Restart bgpd so the module loads (must happen before any BGP config is applied)]
17:17:34   TASK [Loopback, unnumbered spine ports, /31s to the route servers and GPU servers]
17:17:40   TASK [Render and apply FRR config]
17:17:41   TASK [ansible.builtin.command]
17:17:41   PLAY [Configure route servers]
17:17:41   TASK [Render and apply FRR config]
17:17:42   TASK [ansible.builtin.command]
17:17:43   PLAY [Configure GPU servers (one NIC per rail; eth<L> goes to leaf<L>)]
17:17:43   TASK [Addresses, a route to each rail, and a per-NIC table so traffic leaves the NIC it is sourced from]
17:17:43   PLAY [Re-send BGP updates so policy changes take effect on a running lab]
17:17:43   TASK [Soft clear]
17:17:44 waiting for 4 BGP peers up on leaf1 (up to 300s)
17:17:44   done: 4 BGP peers up on leaf1 after 0.0s
17:17:44 ansible-playbook scale.yml scale_action=add scale_count=10000 scale_leaf=leaf2
17:17:45   PLAY [Build inventory from the lab counts]
17:17:45   TASK [Spines]
17:17:45   TASK [Leaves]
17:17:45   TASK [Route servers]
17:17:45   TASK [GPU servers]
17:17:45   PLAY [Inject GPU routes]
17:17:45   TASK [Render static routes (blackhole is fine, this only exercises the control plane)]
17:17:46   TASK [Apply them in one batch]
17:17:50 waiting for 40,000 BGP paths on leaf1 (up to 300s)
17:17:51   done: 40,000 BGP paths on leaf1 after 1.0s

traditional: leaf1 holds 40,069 BGP paths for 10,000 GPU routes (same routes, more copies)
PASSED
tests/test_bgp_paths.py::test_route_updates_on_spine1_restart[traditional] 
--------------------------------------------------------------------------------------- live log call ----------------------------------------------------------------------------------------
17:17:51 restarting BGP on spine1
17:17:52 waiting for spine1 session down (up to 30s)
17:17:52   done: spine1 session down after 0.0s
17:17:52 waiting for spine1 back with all its routes (up to 120s)
17:17:56   done: spine1 back with all its routes after 4.0s

traditional: spine1 re-sent 10,016 routes to leaf1
PASSED
tests/test_bgp_paths.py::test_route_count[pivot] 
--------------------------------------------------------------------------------------- live log setup ---------------------------------------------------------------------------------------
17:17:56 ansible-playbook scale.yml scale_action=del scale_count=10000 scale_leaf=leaf2
17:17:56   PLAY [Build inventory from the lab counts]
17:17:56   TASK [Spines]
17:17:56   TASK [Leaves]
17:17:56   TASK [Route servers]
17:17:56   TASK [GPU servers]
17:17:56   PLAY [Inject GPU routes]
17:17:56   TASK [Render static routes (blackhole is fine, this only exercises the control plane)]
17:17:57   TASK [Apply them in one batch]
17:18:00 ansible-playbook configure.yml mode=pivot
17:18:00   PLAY [Build inventory from the lab counts]
17:18:00   TASK [Spines]
17:18:00   TASK [Leaves]
17:18:00   TASK [Route servers]
17:18:00   TASK [GPU servers]
17:18:01   PLAY [Wait for the SONiC switches and start the daemons sonic-vs leaves off]
17:18:01   TASK [Wait until orchagent, FRR and all 32 ports are up]
17:18:02   TASK [Restart lldpd (sonic-vs starts it without its control socket)]
17:18:05   TASK [Start bfdd (shipped but not started in sonic-vs)]
17:18:06   PLAY [Configure spines]
17:18:06   TASK [Loopback, and one unnumbered port per leaf (Ethernet0 = leaf1, Ethernet4 = leaf2, ...)]
17:18:09   TASK [Render and apply FRR config]
17:18:10   TASK [ansible.builtin.command]
17:18:11   PLAY [Configure leaves]
17:18:11   TASK [Load FRR's BMP module into bgpd on the leaves listed in bmp_leaves]
17:18:11   TASK [Restart bgpd so the module loads (must happen before any BGP config is applied)]
17:18:11   TASK [Loopback, unnumbered spine ports, /31s to the route servers and GPU servers]
17:18:17   TASK [Render and apply FRR config]
17:18:18   TASK [ansible.builtin.command]
17:18:19   PLAY [Configure route servers]
17:18:19   TASK [Render and apply FRR config]
17:18:20   TASK [ansible.builtin.command]
17:18:20   PLAY [Configure GPU servers (one NIC per rail; eth<L> goes to leaf<L>)]
17:18:20   TASK [Addresses, a route to each rail, and a per-NIC table so traffic leaves the NIC it is sourced from]
17:18:21   PLAY [Re-send BGP updates so policy changes take effect on a running lab]
17:18:21   TASK [Soft clear]
17:18:22 waiting for 6 BGP peers up on leaf1 (up to 300s)
17:18:22   done: 6 BGP peers up on leaf1 after 0.0s
17:18:22 ansible-playbook scale.yml scale_action=add scale_count=10000 scale_leaf=leaf2
17:18:22   PLAY [Build inventory from the lab counts]
17:18:22   TASK [Spines]
17:18:22   TASK [Leaves]
17:18:22   TASK [Route servers]
17:18:22   TASK [GPU servers]
17:18:22   PLAY [Inject GPU routes]
17:18:22   TASK [Render static routes (blackhole is fine, this only exercises the control plane)]
17:18:23   TASK [Apply them in one batch]
17:18:28 waiting for 20,000 BGP paths on leaf1 (up to 300s)
17:18:28   done: 20,000 BGP paths on leaf1 after 0.0s

pivot: leaf1 holds 20,045 BGP paths for 10,000 GPU routes (same routes, more copies)
PASSED
tests/test_bgp_paths.py::test_route_updates_on_spine1_restart[pivot] 
--------------------------------------------------------------------------------------- live log call ----------------------------------------------------------------------------------------
17:18:28 restarting BGP on spine1
17:18:28 waiting for spine1 session down (up to 30s)
17:18:28   done: spine1 session down after 0.0s
17:18:28 waiting for spine1 back with all its routes (up to 120s)
17:18:32   done: spine1 back with all its routes after 4.0s

pivot: spine1 re-sent 4 routes to leaf1
PASSED
------------------------------------------------------------------------------------- live log teardown --------------------------------------------------------------------------------------
17:18:32 ansible-playbook scale.yml scale_action=del scale_count=10000 scale_leaf=leaf2
17:18:32   PLAY [Build inventory from the lab counts]
17:18:32   TASK [Spines]
17:18:32   TASK [Leaves]
17:18:32   TASK [Route servers]
17:18:32   TASK [GPU servers]
17:18:33   PLAY [Inject GPU routes]
17:18:33   TASK [Render static routes (blackhole is fine, this only exercises the control plane)]
17:18:34   TASK [Apply them in one batch]


================================================================================ 4 passed in 73.66s (0:01:13) ================================================================================
(.venv) host server1 │ dir ~/git/sonic-rr │ git pytest-bgp-recovery ✗ uncommitted
➜ 
```

## What I Learned
I'm impressed with the flexibility of BGP with its many knobs. It was cool how Alibaba figured out a solution that worked for them. It doesn't minimize BGP updates as well as Microsoft's, but it still gave them the flexibility and cost-effectiveness they desired, plus GPU address mobility between racks (no new NICs or SONiC software changes required).

Plus I found it interesting that the next-hop for every GPU prefix is the TOR switch it connects to, so this is probably helpful for troubleshooting. If you are leaf1, and have some IP and want to know the first hop switch for that GPU.

I learned the basics of how to set up pytest, define the input for each test and query the 'switch' for output to assert against.

I never realized this, but all the spine switches at the top of the stack whether its 2 or 3 tier should all have the same AS number in order to prevent the ["valley flow"](https://www.ipspace.net/Data_Center_BGP/Autonomous_Systems_and_AS_Numbers) problem.  Even [RFC7938](https://www.rfc-editor.org/rfc/rfc7938.html) mentions it on Section 5.2.1. 

I will learn Segment Routing over IPv6 (SRv6) soon, and if I can emulate it, I will.