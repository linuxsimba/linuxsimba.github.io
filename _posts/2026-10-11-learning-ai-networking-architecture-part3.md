---
title: "Learning Neural Network Infrastructure - Part 3"
tags: ["ai", "networking", "ecmp", "clos", "optics", "broadcom"]
---


This is part 3 of my series documenting my journey learning about neural network (AI) infrastructure. In [part two]({% post_url 2026-10-09-learning-ai-networking-architecture-part2 %}), I went through AI training workflows and which parts of the workflow hit the network.

In this post, I go through the routing side of AI networks: with a focus on Equal-Cost Multi-Path (ECMP) routing and why AI network engineers care so much about ECMP. 


## L3 CLOS Topologies - Frontend + Backend

In [part two]({% post_url 2026-10-09-learning-ai-networking-architecture-part2 %}), I described the split between the frontend and backend networks, Tom Emmons from Arista in his 2025 presentation [Arista Networking for AI: The Ethernet Backplane](https://www.youtube.com/watch?v=S5JwBHUgZss&t=1029s) said something interesting about frontend networks. He said the frontend "looks like a traditional data center. You just care about it a lot more, because you have billions of dollars of hardware behind it instead of millions." With the rise of inference I believe frontend networks are going to start to matter just as much as backend networks.  So it seems like RAG , KV caches and Prefills may play a greater role in the AI networking design? I will  update this blog post as I learn more about this. 

What is  consistent though between frontend and backend network is the foundation of an AI network that is the L3 CLOS topology (leaf-spine). I suspect its the cost that has governed this decision. Ethernet/IP is a well known technology, you can find engineers to troubleshoot it and manage it, L3 CLOS deployments can be easily automated because both servers and switches are programmable using infrastracture as code tooling.

Why L3 and not one big Layer 2 network? The best reference I found is [RFC 7938 - Use of BGP for Routing in Large-Scale Data Centers](https://datatracker.ietf.org/doc/html/rfc7938), written in 2016 by Petr Lapukhov et.al. The authors stated, that based on their experience The operational simplicity and network stability is achieved with a L3 CLOS with a small number of staff. 

### IPv4 or IPv6?

During Emmons' talk, someone in the audience asked: ["Is IPv6 required for back-end networks?"](https://www.youtube.com/watch?v=S5JwBHUgZss&t=1466s) I thought this was a great question.

I think based on Emmons answer, it makes sense, at least to me, to use IPv6 for address simplicity. Especially now that you can use infrastructure as code and easily create non-overlapping addresses. 

He also said you won't see IPv6 in scale-up networks. My guess is that any additional payload info increases latency.


## Scale Up - Ethernet's Next Frontier?

In part two, I described the scale-up network as NVLink, connecting GPUs inside a server or rack. Emmons said [Arista believes Ethernet is a strong competitor for the scale-up fabric](https://www.youtube.com/watch?v=S5JwBHUgZss&t=1219s). His reasons were Ethernet is cost-effective and from a supply chain perpective many vendors to pick from.

But scale-up is hard for Ethernet.

* **Bandwidth**: a GPU might have 400G of NIC bandwidth for scale-out, [but 3.6 Tb/s of scale-up bandwidth](https://www.nvidia.com/en-gb/data-center/nvlink/). That's 8 to 9 times more.
* **Cost and Power**: Building a power efficient ethernet scale up network is a current challenge
* **Small packets**: GPUs talk to each other in the scale-up network using memory load and store operations, which produce 256 byte cache line sized packets. Traditional Ethernet is not efficient at that size.

But Arista continues to venture into scale-up networking. I need to investigate this, but I believe inference doesn't require as much GPU-to-GPU bandwidth during its operations as neural net training does. 

So with Arista's October 7, 2026 announcement that it supports [ESUN (Ethernet for Scale-Up Networking)](https://blogs.arista.com/blog/next-gen-scale-up-networking-for-ai-fabrics), perhaps Arista will pitch Ethernet as the cost-effective way to build scale-up networks for AI inference?


## Network Depth - Why AI Fabrics Prefer 2 Tiers

Back to the scale-out network. How deep should a CLOS be? I kept hearing "2-tier" and "3-tier" in these videos, so here are the terms as I understand them:

* **Single tier**: one big modular switch. Every GPU connects to the same chassis.
* **2-tier**: leaf-spine. A packet goes leaf, spine, leaf. This is a 3-stage CLOS network
* **3-tier**: leaf, spine, super spine. This is a 5-stage CLOS network.

From the videos, AI network architects prefer 2 tiers whenever possible. The reasoning is:

* Fewer tiers are cheaper, more performant and lower power
* It's a cost issue. **Every tier adds two more optics per GPU.** Every GPU has a 400G or 800G port, so that's a lot of optics.
* Every tier makes load balancing harder.
* Every tier adds more congestion points for traffic to run into. AI scale-out networks, from what I've heard so far, still struggle with congestion management.

The way to stay at 2 tiers is a switch with a high radix (more ports). 

Meta's [SIGCOMM 2024 talk](https://www.youtube.com/watch?v=oDBMv_5rbQg&t=429s) by Adithya Gangidi shows the same thinking in practice. Meta's "AI Zone" is a 2-tier CLOS of 4,000 GPUs with full bisection bandwidth. 


## ECMP - A History and Current Challenges

Equal-Cost Multi-Path (ECMP) routing has been around a long time. [RFC 2991](https://datatracker.ietf.org/doc/html/rfc2991) and [RFC 2992](https://datatracker.ietf.org/doc/html/rfc2992) described multipath forwarding and the hash-based method back in 2000. In a CLOS network, every leaf has multiple equal-cost paths to every other leaf, one through each spine. ECMP is what spreads the traffic across them.

Hugh Holbrook of Arista explained [how it works](https://www.youtube.com/watch?v=0roIi1pscts&t=987s) in his 2024 NANOG 92 keynote. The switch feeds the 5-tuple (source IP, destination IP, protocol, source port and destination port) into a hash function in hardware. The result maps to one of the ECMP paths. Every packet in a flow has the same 5-tuple, so every packet in the flow takes the same path and arrives in order. 

### Why AI training breaks ECMP

Holbrook walked through a [simple example](https://www.youtube.com/watch?v=0roIi1pscts&t=1023s) that shows how a small number of high-bandwidth flows can overload a link. With only 8 flows per server, one uplink ended up carrying [140% of its capacity](https://www.youtube.com/watch?v=0roIi1pscts&t=1233s), and every flow on that link slowed down. With normal TCP traffic, that's not a big deal. There are thousands of flows, they average out across the links, and no application waits on the slowest one. In the AI training universe, it's a big deal. Collectives [run at the speed of the slowest link](https://www.youtube.com/watch?v=0roIi1pscts&t=1334s), so one overloaded link slows down every GPU in the job, on every iteration. With a training run of 1,000+ GPUs, that's a lot of wasted time and power. And if a link actually fails, the job has to [roll back to its last checkpoint](https://www.youtube.com/watch?v=S5JwBHUgZss&t=390s), which can cost hundreds or thousands of hours of GPU time.


And AI training has few flows. In the SIGCOMM talk, Gangidi said that out of the box, Meta saw [less than 10 flows per collective (operation)](https://www.youtube.com/watch?v=oDBMv_5rbQg&t=535s), and with that few flows, hash-based ECMP "will perform very poorly." On the Packet Pushers podcast about MRC, a Broadcom engineer summed it up: ["tail latency is a killer for RoCE"](https://www.youtube.com/watch?v=AQhoTd9rf60&t=355s).

### How the industry is fixing ECMP

Here's how I understand the progression of solutions, from simplest to most involved.

#### 1. Make more flows

Creating more flows is one solution AI network engineers tried. Meta took the messages, or "chunks" as the [NCCL paper I referenced in part two](https://arxiv.org/html/2507.04786v3) calls them, and found a way to [send each chunk on a different queue pair](https://www.youtube.com/watch?v=oDBMv_5rbQg&t=676s), round robin. Based on the [RoCEv2 specification](https://pdfcoffee.com/annex17-rocev2-pdf-free.html), I believe each connected queue pair keeps a fixed UDP source port, and different queue pairs usually get different ports. More queue pairs means more UDP source ports. That creates higher entropy that switches can use when hashing traffic across the 2-tier network.

#### 2. Dynamic Load Balancing (DLB)

The next step is to let the switch chip look at how busy each link is. Broadcom calls it [Dynamic Load Balancing](https://investors.broadcom.com/news-releases/news-release-details/broadcom-ships-tomahawk-5-industrys-highest-bandwidth-switch). It is a feature of the Tomahawk 5 chip which was launched in 2022. 

Here is how I understand it. Plain ECMP only looks at packet headers. DLB also tracks how much traffic each uplink has recently sent and how deep its queue is, and picks the least busy link. Most DLB deployments work on **flowlets**. A flowlet is a burst of packets in a flow followed by a short pause. If the pause is longer than the delay difference between the paths, the next burst can safely move to a different link without arriving out of order. AI traffic has natural pauses between compute and communication, so flowlets fit well.

Emmons said DLB is [the most common solution deployed today in Arista switches](https://www.youtube.com/watch?v=S5JwBHUgZss&t=635s). He called it "a fundamentally greedy algorithm." It does a great job balancing traffic leaving the leaf, but it can't fix imbalance from the spine down to the destination leaf".

> I'm still looking for good documentation on how SONiC and FBOSS expose DLB. I'll update this post when I find it.

#### 3. Global load balancing

DLB only sees its own links. The next step is to share congestion information between switches. Broadcom's Tomahawk 5 [Global Load Balancing](https://investors.broadcom.com/news-releases/news-release-details/broadcom-now-shipping-worlds-first-512-tbps-switch-production) uses "distributed inter-switch communication of congestion information to choose the best global path." The Tomahawk 6 extends this as [Cognitive Routing 2.0](https://investors.broadcom.com/news-releases/news-release-details/broadcom-ships-tomahawk-6-worlds-first-1024-tbps-switch).

#### 4. Packet spraying (MRC)

Packet spraying sends the packets of a single flow across all the paths, instead of pinning the whole flow to one path. 

The catch is that packets arrive out of order, so the receiving NIC has to handle it. Holbrook showed that spraying fixes his example: the [worst link drops to about 90% and efficiency goes to 99.98%](https://www.youtube.com/watch?v=0roIi1pscts&t=1380s). Emmons said packet spraying is [where the industry is heading](https://www.youtube.com/watch?v=S5JwBHUgZss&t=846s), and multiple customers have deployed it. "It's just a matter of the NICs getting there."

This packet spraying workflow is the basis for Multipath Reliable Connection (MRC). In the [Packet Pushers episode](https://www.youtube.com/watch?v=AQhoTd9rf60&t=98s), three Broadcom engineers explained that Multipatch Reliable Connection (MRC) is an open extension to RoCEv2, driven by Microsoft and OpenAI with AMD, Intel, NVIDIA and Broadcom. The NIC [puts a different entropy value on each packet](https://www.youtube.com/watch?v=AQhoTd9rf60&t=1259s), and unmodified ECMP switches spray them across every path. It is not clear to me yet if this is implemented today in any NIC. 


#### 5. Ultra Ethernet

The [UEC approach](https://www.youtube.com/watch?v=0roIi1pscts&t=487s) to fixing ECMP problems is similar to MRC: spray the packets across all the paths. When a switch queue is full, instead of dropping a packet, the switch trims it down to 64 bytes, changes the DSCP value and sends it to the receiver on a high-priority queue. This way the receiver knows right away what was lost. UEC also adds a mechanism where the receiver hands out credits that tell each sender how much data it can send. Surprisingly, UEC doesn't require new switches. Holbrook said a switch can be ["completely compliant"](https://www.youtube.com/watch?v=0roIi1pscts&t=901s) by supporting Ethernet as it is today. Trimming is optional and needs switch support.

Both solutions require NICs that support their protocol. For either UEC's ECMP changes or OCP's MRC I believe a firmware update to the Broadcom Tomahawk switch is the only thing required to enable packet trimming. I'm not sure if that's already in place SoNIC or FBOSS.



_References:_
* _[Arista Networking for AI: The Ethernet Backplane](https://www.youtube.com/watch?v=S5JwBHUgZss) - Tom Emmons, Arista_
* _[Keynote: Networking for AI and HPC, and Ultra Ethernet](https://www.youtube.com/watch?v=0roIi1pscts) - Hugh Holbrook, Arista, NANOG 92 (2024)_
* _[RDMA over Ethernet for Distributed AI Training at Meta Scale](https://www.youtube.com/watch?v=oDBMv_5rbQg) - Adi Gangidi, Meta, SIGCOMM 2024_
* _[HN844: Multipath Reliable Connection (MRC)](https://www.youtube.com/watch?v=AQhoTd9rf60) - Packet Pushers_
* _[Reducing Job Completion Time in AI/ML Clusters with Broadcom DNX](https://www.youtube.com/watch?v=XLz2_dOw1U0) - Tech Field Day_
* _[Gilad Shainer, NVIDIA: Scale Up, Scale Out & The Future of AI Networks](https://www.youtube.com/watch?v=3MplvKTuwio) - theCUBE_
* _[Networking for AI: Why Every Network Engineer Should Pay Attention in 2026](https://www.youtube.com/watch?v=mkUP_iQNj2s) - The Art of Network Engineering_
* _[RFC 7938: Use of BGP for Routing in Large-Scale Data Centers](https://datatracker.ietf.org/doc/html/rfc7938)_
* _[RFC 2992: Analysis of an Equal-Cost Multi-Path Algorithm](https://datatracker.ietf.org/doc/html/rfc2992)_
* _[OCP Summit 2025: The open future of networking hardware for AI](https://engineering.fb.com/2025/10/13/data-infrastructure/ocp-summit-2025-the-open-future-of-networking-hardware-for-ai/) - Meta_
* _[Ethernet Standards for Scale-Up AI: An Overview of ESUN, SUE, and UALink](https://www.synopsys.com/articles/ethernet-standards-scale-up-ai.html) - Synopsys_
