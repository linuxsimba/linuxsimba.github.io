---
title: "Learning Neural Network Infrastructure - Part 3"
tags: ["ai", "networking", "ecmp", "clos", "optics", "broadcom"]
---


This is part 3 of my series documenting my journey learning about neural network (AI) infrastructure. In [part two]({% post_url 2026-10-09-learning-ai-networking-architecture-part2 %}), I went through AI training workflows and which parts of the workflow hit the network.

In this post, I go through the physical and routing side of AI networks: the topologies, the connections between servers and switches, and ECMP and why AI network engineers care so much about it. I also take a look at what Broadcom switch chips offer in 2026, since Broadcom is the main supplier of switch chips for commodity Ethernet switches. From what I've found, hyperscalers like Meta and Microsoft mostly buy white-box switches and run their own software, like FBOSS and SONiC. Enterprises mostly buy branded switches, but many of those use Broadcom chips inside too.


## L3 CLOS Topologies - Frontend + Backend

In part two, I described the split between the frontend and backend networks, Tom Emmons from Arista in his 2025 presentation [Arista Networking for AI: The Ethernet Backplane](https://www.youtube.com/watch?v=S5JwBHUgZss&t=1029s) said something interesting about frontend networks. He said the frontend "looks like a traditional data center. You just care about it a lot more, because you have billions of dollars of hardware behind it instead of millions." I can't find the reference now, but I think that with the rise of inference traffic frontend networks will begin to matter just as much as backend networks in the time when most of the AI traffic was just training.  So it seems like RAG , KV caches and Prefills may play a greater role in the AI networking design? I will  update this blog post as I learn more about this. 

What is  consistent though between frontend and backend network is the foundation of an AI network is L3 CLOS topology (leaf-spine). I suspect its the cost that has governed this decision. Ethernet/IP is a well known technology, you can find engineers to troubleshoot it and manage it, L3 CLOS deployments can be easily automated because both servers and switches are not programmable using infrastracture as code tooling.

Why L3 and not one big Layer 2 network? The best reference I found is [RFC 7938 - Use of BGP for Routing in Large-Scale Data Centers](https://datatracker.ietf.org/doc/html/rfc7938), written in 2016 by Petr Lapukhov et.al. The authors stated, that based on their experience The operational simplicity and network stability is achieved with a L3 CLOS with a small number of staff. 

### IPv4 or IPv6?

During Emmons' talk, someone in the audience asked: ["Is IPv6 required for back-end networks?"](https://www.youtube.com/watch?v=S5JwBHUgZss&t=1466s) I thought this was a great question, because every GPU gets its own 400G or 800G port, and that is a lot of ports to number.

His answer: it's Ethernet, so anything works. IPv4 works in all of these networks, and the frontend is "almost certainly going to be IPv6." The real problem is whether you as a company can find IPv4 addresses for all of the ports. The backend is not exposed to the internet, so private addresses work. But [many of the largest customers are using IPv6 in the backend anyway](https://www.youtube.com/watch?v=S5JwBHUgZss&t=1518s), because "the penalty on a 4,000 byte packet isn't that much," and it makes address provisioning a lot easier.

He also said you won't see IPv6 in scale-up networks. That led me down the next rabbit hole.


## Scale Up - Ethernet's Next Frontier?

In part two, I described the scale-up network as NVLink, connecting GPUs inside a server or rack. Emmons said [Arista believes Ethernet is a strong competitor for the scale-up fabric](https://www.youtube.com/watch?v=S5JwBHUgZss&t=1219s). His reasons: Ethernet is cost-effective, there are multiple chip vendors to choose from, it uses the same tooling as the rest of your network, and "you can actually hire engineers who understand Ethernet networking." I laughed at that one.

But scale-up is hard for Ethernet. [He listed the challenges](https://www.youtube.com/watch?v=S5JwBHUgZss&t=1308s):

* **Bandwidth**: a GPU might have 400G of NIC bandwidth for scale-out, but 3.6 Tb/s of scale-up bandwidth. That's 8 to 9 times as many ports.
* **Lossless**: building end-to-end reliability into every GPU costs too many gates on the chip, so engineers want the network to be lossless instead.
* **Small packets**: GPUs talk to each other in the scale-up network using memory load and store operations, which produce 256 byte cache line sized packets. Traditional Ethernet is not efficient at that size.

This is where it gets interesting. OCP has a workstream called ESUN (Ethernet for Scale-Up Networking). [One of the biggest things ESUN did](https://www.youtube.com/watch?v=S5JwBHUgZss&t=1542s) was get rid of the IP header completely. You get an Ethernet header followed by a small ESUN tag that carries the routing information: an entropy value, a TTL and a QoS field. He described it as "forwarding that looks a lot like routing but using a MAC address header." A 14 byte Ethernet header plus a 4 byte tag saves 16 bytes compared to an IPv4 header. The person asking the question replied, "we've seen this movie before... MPLS comes to mind." Network engineers never forget.

#### _"Are OCP and Ultra Ethernet competing on scale-up?"_

I assumed OCP and the Ultra Ethernet Consortium (UEC) had two competing standards for scale-up. According to Emmons, [that's not the case](https://www.youtube.com/watch?v=S5JwBHUgZss&t=1604s). He said "the groups are very much trying to work together." The ESUN 1.0 spec relies on credit-based flow control (CBFC) and link layer retry (LLR), "two technologies UEC standardized." UEC hasn't been trying to build a complete scale-up story, and ESUN wraps those pieces together into a recipe. He also pointed out that the founding companies of both groups are basically the same. Meta's [OCP Summit 2025 networking post](https://engineering.fb.com/2025/10/13/data-infrastructure/ocp-summit-2025-the-open-future-of-networking-hardware-for-ai/) confirms ESUN aligns with UEC and IEEE, and lists AMD, Arista, ARM, Broadcom, Cisco, HPE, Marvell, Meta, Microsoft, NVIDIA, OpenAI and Oracle as founding participants.

That said, there are several scale-up efforts out there. A [Synopsys article from January 2026](https://www.synopsys.com/articles/ethernet-standards-scale-up-ai.html) gives a good overview of three of them: ESUN, SUE (Scale-Up Ethernet, a framework contributed to OCP with a compressed "AI Fabric Header") and UALink (a consortium standard for memory semantics between accelerators). Synopsys sees them as complementary. NVLink is still proprietary.

So is scale-up Ethernet's next frontier? Emmons thinks so. He said [every customer building custom silicon is looking towards Ethernet](https://www.youtube.com/watch?v=S5JwBHUgZss&t=1785s) for scale-up, and he expects "almost complete dominance on the custom silicon side," and then "we'll see how that trickles into AMD and NVIDIA." I think scale-up is the next battleground for Ethernet. We'll see.


## Network Depth - Why AI Fabrics Prefer 2 Tiers

Back to the scale-out network. How deep should a CLOS be? I kept hearing "2-tier" and "3-tier" in these videos, so here are the terms as I understand them:

* **Single tier**: one big modular switch. Every GPU connects to the same chassis.
* **2-tier**: leaf-spine. A packet goes leaf, spine, leaf. Because the packet crosses 3 switches, this is also called a **3-stage (folded) CLOS**.
* **3-tier**: leaf, spine, super spine. This is a 5-stage CLOS.

From the videos, AI network architects prefer 2 tiers whenever possible. Emmons explained that [the largest deployments need 3 tiers](https://www.youtube.com/watch?v=S5JwBHUgZss&t=508s) because "you physically can't fit it" in two. Most customers fit in a 2-tier network, and small buildouts can fit in a single modular switch. His reasoning:

* "Fewer tiers are cheaper, more performant and lower power."
* **Every tier adds two more optics per GPU.** Every GPU has a 400G or 800G port, so that's a lot of optics.
* Every tier makes load balancing harder.
* Every tier adds more congestion points for traffic to run into.

The way to stay at 2 tiers is a switch with a high radix (more ports). He said using a [modular spine chassis instead of a fixed switch](https://www.youtube.com/watch?v=S5JwBHUgZss&t=573s) takes you from 128 400G ports to around 1,000, a 10x increase in the size of a 2-tier network.

Meta's [SIGCOMM 2024 talk](https://www.youtube.com/watch?v=oDBMv_5rbQg&t=429s) by Adi Gangidi shows the same thinking in practice. Meta's "AI Zone" is a 2-tier CLOS of 4,000 GPUs with full bisection bandwidth. For GenAI training, they needed more GPUs, so [they connected 8 AI Zones with a third tier](https://www.youtube.com/watch?v=oDBMv_5rbQg&t=460s) at 1:7 oversubscription. They made the job scheduler topology-aware so the oversubscribed third tier was "never a problem." So 2 tiers by default, and a third tier only when they had no choice.

Hugh Holbrook put the optics part in perspective in his [NANOG keynote](https://www.youtube.com/watch?v=0roIi1pscts&t=2697s): "100,000 GPUs in a two-tier network: 400,000 transceivers, 200,000 links." Which brings me to optics.


## Optics - A History and Which Ones to Use Where

I didn't expect optics to come up so much in these videos. But in AI networking, the optics conversation is all about watts.

Emmons opened his talk by saying [almost every AI buildout is limited by power](https://www.youtube.com/watch?v=S5JwBHUgZss&t=128s). The customer asks "how many GPUs can I fit in this 20 megawatt building?" Every watt the network uses is a GPU you can't install. He said "the biggest contributor to power in your network is optics." The goal is to keep the network [under 10% of the total power](https://www.youtube.com/watch?v=S5JwBHUgZss&t=475s), and the optics you pick can make a 20 to 50% difference in network power. Gilad Shainer from NVIDIA said in a [theCUBE interview](https://www.youtube.com/watch?v=3MplvKTuwio&t=1966s) that optics power can go "almost to 10% of the compute capacity."

Power is not the only problem. Holbrook said [optics have a mean time between failures of about 5 years](https://www.youtube.com/watch?v=0roIi1pscts&t=2697s). With 400,000 transceivers, failures happen "fairly regularly." And as I learned in [part two]({% post_url 2026-10-09-learning-ai-networking-architecture-part2 %}), when one link has a problem, the whole training job waits.

### Copper first

Copper is still the first choice wherever the distance is short enough. Meta places their top of rack switch in the rack, so the GPU servers [connect with short copper DAC cables instead of optics](https://www.youtube.com/watch?v=oDBMv_5rbQg&t=495s), which means fewer failures. Shainer said ["copper is zero power"](https://www.youtube.com/watch?v=3MplvKTuwio&t=1904s), and that's why NVIDIA uses copper for scale-up inside the rack, with liquid cooling to pack the rack tight enough for copper to reach. Scale-out has to use optics because of distance. Holbrook said backend links are [150 to 300 meters](https://www.youtube.com/watch?v=0roIi1pscts&t=645s), with 400G per GPU moving to 800G.

### Co-packaged optics

The new thing I kept hearing about is co-packaged optics (CPO). With a pluggable optic, the switch chip has to drive the electrical signal across the circuit board to the optic in the front panel. That takes power. Shainer explained that [CPO moves the optical engine into the switch chip package](https://www.youtube.com/watch?v=3MplvKTuwio&t=2003s), so the signal doesn't have to travel across the board. On the Art of Network Engineering podcast, they said those copper traces to the front panel are [becoming the bottleneck](https://www.youtube.com/watch?v=mkUP_iQNj2s&t=1575s) as speeds go up.

Why is CPO becoming more popular? Power and reliability. NVIDIA claims CPO [cuts scale-out network power by 3.5x](https://www.youtube.com/watch?v=3MplvKTuwio&t=2036s), which lets you fit 3x more GPUs in the same power budget. Broadcom says the [Tomahawk 6 CPO version](https://investors.broadcom.com/news-releases/news-release-details/broadcom-ships-tomahawk-6-worlds-first-1024-tbps-switch) provides "the lowest power and latency while reducing link flaps," and builds on the CPO versions of Tomahawk 4 and 5 they already shipped.

The catch? With pluggables, if one optic fails, you replace one optic. With CPO, the optics are part of the switch. The Art of Network Engineering hosts said operators may [wait until four or six ports have gone bad](https://www.youtube.com/watch?v=mkUP_iQNj2s&t=1758s) before swapping the whole switch, in exchange for a big reduction in power.

### Which one to use where

Here's my summary of what I learned:

| Where | What's used | Why |
|-------|-------------|-----|
| Scale-up (GPUs in a rack) | Copper | Zero power, reliable, cheap. Liquid cooling makes the rack dense enough for copper to reach. |
| GPU to top of rack leaf | Copper DAC, when the leaf is in the rack | Fewer failures than optics |
| Leaf to spine (scale-out) | Pluggable optics today, CPO arriving | 150 to 300 meter distances, 400G moving to 800G |
| Dense spines in power-limited buildings | CPO | Lower power, fewer link flaps |
| Scale-across (between buildings) | Long reach optics | Emmons: ["the lowest power optic that can go the distance"](https://www.youtube.com/watch?v=S5JwBHUgZss&t=1896s) |


## ECMP - A History and Current Challenges

Now the part I promised in part two. Equal-Cost Multi-Path (ECMP) routing has been around a long time. [RFC 2991](https://datatracker.ietf.org/doc/html/rfc2991) and [RFC 2992](https://datatracker.ietf.org/doc/html/rfc2992) described multipath forwarding and the hash-based method back in 2000. In a CLOS network, every leaf has multiple equal-cost paths to every other leaf, one through each spine. ECMP is what spreads the traffic across them.

Holbrook explained [how it works](https://www.youtube.com/watch?v=0roIi1pscts&t=987s). The switch feeds the 5-tuple (source IP, destination IP, protocol, source port and destination port) into a hash function in hardware. The result maps to one of the ECMP paths. Every packet in a flow has the same 5-tuple, so every packet in the flow takes the same path and arrives in order. That matters because TCP and RDMA treat out-of-order packets as packet loss.

This "works really well if there are a lot of flows." Web traffic is thousands of small flows, and they average out nicely across the links. AI training traffic is not.

### Why AI training breaks ECMP

Holbrook walked through a [simple example](https://www.youtube.com/watch?v=0roIi1pscts&t=1023s) that made it click for me. Take one top of rack switch with 32 GPU servers, and 32 uplinks to 32 spines. No oversubscription. Every server sends traffic at 80% of its link speed, and ECMP hashes the flows across the uplinks.

![ECMP flow hashing example from the NANOG keynote](/images/ecmp-flow-hashing-nanog.png)

* With **80 flows** per server, the flows average out and the network runs at 99.95% efficiency.
* With **8 flows** per server, the average efficiency is still about 97%. But the [worst link ends up with 14 flows](https://www.youtube.com/watch?v=0roIi1pscts&t=1233s), 140% of its capacity, so it only runs at about 70% efficiency.

Who cares about the worst link if the average is fine? AI training does. Collectives like ring all-reduce [run at the speed of the slowest link](https://www.youtube.com/watch?v=0roIi1pscts&t=1334s). One overloaded link slows down every GPU in the job.

And AI training really does have very few flows. In the SIGCOMM talk, Gangidi said that out of the box, Meta saw [less than 10 flows per collective](https://www.youtube.com/watch?v=oDBMv_5rbQg&t=535s), and with that few flows, hash-based ECMP "will perform very poorly." This is the "low entropy" problem I mentioned in part two. On the Packet Pushers podcast about MRC, a Broadcom engineer summed it up: ["tail latency is a killer for RoCE"](https://www.youtube.com/watch?v=AQhoTd9rf60&t=355s).

### How the industry is fixing ECMP

Here's how I understand the progression of solutions, from simplest to most involved.

#### 1. Make more flows

If the problem is too few flows, create more. Meta tried several things first. [Static routing gave them](https://www.youtube.com/watch?v=oDBMv_5rbQg&t=562s) "very variable performance." They then [built the network at 1:2 undersubscription](https://www.youtube.com/watch?v=oDBMv_5rbQg&t=600s) so hash collisions didn't matter, which Gangidi called "a very poor solution, expensive solution." Centralized traffic engineering worked well inside an AI Zone, but [got too complex at 3 tiers](https://www.youtube.com/watch?v=oDBMv_5rbQg&t=657s), so they went back to ECMP.

What finally worked was what they call [enhanced ECMP](https://www.youtube.com/watch?v=oDBMv_5rbQg&t=676s). The switches hash on the RDMA queue pair (QP) ID, and the collective library spreads each message across many queue pairs, "making one flow appear as many." The number of QPs per job went from tens to hundreds or thousands. They trained Llama 3 on it. I like this fix because the switches stay simple.

#### 2. Dynamic Load Balancing (DLB)

The next step is to let the switch chip look at how busy each link is. Dynamic Load Balancing started as a Broadcom switch chip feature, and other chip vendors have their own version. Broadcom listed ["dynamic load balancing"](https://investors.broadcom.com/news-releases/news-release-details/broadcom-ships-tomahawk-5-industrys-highest-bandwidth-switch) as an AI feature of the Tomahawk 5 when it launched in 2022.

Here is how I understand it. Plain ECMP only looks at packet headers. DLB also tracks how much traffic each uplink has recently sent and how deep its queue is, and picks the least busy link. Most DLB deployments work on **flowlets**. A flowlet is a burst of packets in a flow followed by a short pause. If the pause is longer than the delay difference between the paths, the next burst can safely move to a different link without arriving out of order. AI traffic has natural pauses between compute and communication, so flowlets fit well.

Emmons said DLB is [the most common solution deployed today](https://www.youtube.com/watch?v=S5JwBHUgZss&t=635s). He called it "a fundamentally greedy algorithm." It does a great job balancing traffic leaving the leaf, but it can't fix imbalance from the spine down to the destination leaf, because each switch only sees its own links. Still, he said it's "simple and generally good enough" for most customers. Meta's results agree. Gangidi said their flowlet data was ["rather encouraging"](https://www.youtube.com/watch?v=oDBMv_5rbQg&t=1067s), close to traffic engineering performance, with the operational simplicity of ECMP.

> I'm still looking for good documentation on how SONiC and FBOSS expose DLB. I'll update this post when I find it.

#### 3. Global load balancing

DLB only sees its own links. The next step is to share congestion information between switches. Broadcom's Tomahawk 5 [Global Load Balancing](https://investors.broadcom.com/news-releases/news-release-details/broadcom-now-shipping-worlds-first-512-tbps-switch-production) uses "distributed inter-switch communication of congestion information to choose the best global path." The Tomahawk 6 extends this as [Cognitive Routing 2.0](https://investors.broadcom.com/news-releases/news-release-details/broadcom-ships-tomahawk-6-worlds-first-1024-tbps-switch).

#### 4. Packet spraying

Packet spraying sends the packets of a single flow across all the paths, instead of pinning the whole flow to one path. It's not a feature of one vendor, and it's not an NCCL feature either. NCCL can open more connections, like Meta did, but each connection is still one flow. Spraying happens below NCCL, either in the switch (picking a path per packet) or in the NIC (changing the entropy, like the UDP source port, on every packet so plain ECMP spreads them).

The catch is that packets arrive out of order, so the receiving NIC has to handle it. Holbrook showed that spraying fixes his example: the [worst link drops to about 90% and efficiency goes to 99.98%](https://www.youtube.com/watch?v=0roIi1pscts&t=1380s). Emmons said packet spraying is [where the industry is heading](https://www.youtube.com/watch?v=S5JwBHUgZss&t=846s), and multiple customers have deployed it. "It's just a matter of the NICs getting there."

One NIC-side example is MRC (Multipath Reliable Connection). In the [Packet Pushers episode](https://www.youtube.com/watch?v=AQhoTd9rf60&t=98s), three Broadcom engineers explained that MRC is an open extension to RoCEv2, driven by Microsoft and OpenAI with AMD, Intel, NVIDIA and Broadcom. The NIC [puts a different entropy value on each packet](https://www.youtube.com/watch?v=AQhoTd9rf60&t=1259s), and unmodified ECMP switches spray them across every path. The switches are "not MRC aware at all." They called it ["baby Ultra Ethernet"](https://www.youtube.com/watch?v=AQhoTd9rf60&t=893s) and a stop gap until Ultra Ethernet is ready.

#### 5. Scheduled fabrics

The most different approach I found is a scheduled fabric. Broadcom's DNX family (Jericho and Ramon chips) was explained in a [Tech Field Day presentation](https://www.youtube.com/watch?v=XLz2_dOw1U0&t=845s). The leaf switch chops every packet into cells and sprays them across all the fabric links, so "all flows use all links all the time." Before sending, the source leaf [asks the destination for credits](https://www.youtube.com/watch?v=XLz2_dOw1U0&t=1433s), so nothing enters the fabric unless the destination has buffer space for it. No hashing, no hash collisions. Broadcom claims up to [30% better job completion time](https://www.youtube.com/watch?v=XLz2_dOw1U0&t=1326s). The catch is that the cell protocol inside the fabric is Broadcom's, ["not a standard"](https://www.youtube.com/watch?v=XLz2_dOw1U0&t=1460s).

Meta built their own version on FBOSS called the Disaggregated Scheduled Fabric (DSF). According to their [OCP Summit 2025 post](https://engineering.fb.com/2025/10/13/data-infrastructure/ocp-summit-2025-the-open-future-of-networking-hardware-for-ai/), DSF is "a VOQ-based system powered by the open OCP-SAI standard and FBOSS," and their 2-stage design connects up to 18,432 GPUs in a non-blocking fabric.

#### 6. Ultra Ethernet

Finally, Ultra Ethernet. Holbrook's NANOG keynote is the best overview I found. He said RDMA itself is fine: ["it's just a specific implementation"](https://www.youtube.com/watch?v=0roIi1pscts&t=487s), RoCE, that has problems. No multipathing, go-back-N retransmission (one lost packet means resending everything after it), outdated congestion control, and no security. The Ultra Ethernet transport fixes these at the NIC:

* Packets can be [delivered out of order](https://www.youtube.com/watch?v=0roIi1pscts&t=1475s), straight into memory, so the network can spray.
* [Packet trimming](https://www.youtube.com/watch?v=0roIi1pscts&t=1670s): when a switch queue is full, instead of dropping a 4K packet, the switch cuts it down to 64 bytes and forwards it at high priority. The receiver immediately knows a packet was lost.
* [New congestion control](https://www.youtube.com/watch?v=0roIi1pscts&t=1975s), both sender-based and receiver-based.
* [Link layer retry](https://www.youtube.com/watch?v=0roIi1pscts&t=2671s) to fix flaky links without an end-to-end retransmit. Remember those optics failures?

What I found most interesting: ["you can be a completely compliant Ultra Ethernet switch"](https://www.youtube.com/watch?v=0roIi1pscts&t=901s) by supporting Ethernet as it is today. Most of the work is in the NIC.

Here's a summary of the solutions:

| Solution | Where it lives | How it works | The catch |
|----------|----------------|--------------|-----------|
| Enhanced ECMP | Host (collective library) + switch hash on QP | Turn one flow into many | Still hashing, collisions still happen |
| DLB / flowlets | Switch chip | Move flowlets to the least busy local link | Only sees local links |
| Global load balancing | Switch chips sharing congestion info | Pick the best path end to end | Newer, chip specific |
| Packet spraying | Switch or NIC | Every packet takes a different path | NIC must handle out-of-order packets |
| Scheduled fabric (DNX, DSF) | Switch chips | Cells sprayed across all links, credit based | Proprietary fabric protocol |
| Ultra Ethernet | NIC (transport) | Spraying, trimming, new congestion control | Needs new NICs |


## What's Available in 2026 - Tomahawk 5, Tomahawk 6 and Qumran3D

I wanted to understand what the Broadcom switch chips offer today, because so many of these solutions live in the switch silicon.

| Chip | Family | Capacity | What stood out to me |
|------|--------|----------|----------------------|
| [Tomahawk 5](https://investors.broadcom.com/news-releases/news-release-details/broadcom-now-shipping-worlds-first-512-tbps-switch-production) | StrataXGS | 51.2 Tb/s | Dynamic load balancing, Cognitive Routing with global load balancing, link failover in under 500ns, CPO version |
| [Tomahawk 6](https://investors.broadcom.com/news-releases/news-release-details/broadcom-ships-tomahawk-6-worlds-first-1024-tbps-switch) | StrataXGS | 102.4 Tb/s | Cognitive Routing 2.0 (telemetry, congestion control, fast failure detection, packet trimming, global load balancing), UEC compliant, CPO version |
| [Qumran3D](https://www.servethehome.com/broadcom-qumran3d-5nm-25-6t-switch-router-chip/) | StrataDNX | 25.6 Tb/s | Single chip router with deep buffers (HBM in the package), hierarchical traffic manager, line-rate MACsec and IPsec |

The Tomahawk 5 and 6 are the high-radix chips for the leaf-spine backend. That ties back to the 2-tier discussion: more radix, fewer tiers, fewer optics. Packet trimming in the Tomahawk 6 is the same idea Holbrook described for Ultra Ethernet.

The Qumran3D is a different animal. Broadcom markets it as a router for core, edge, peering and data center interconnect, not specifically for AI. But it caught my attention because of what I learned in [part two]({% post_url 2026-10-09-learning-ai-networking-architecture-part2 %}) about scale-across networks. Emmons said most customers use [deep buffers for scale-across](https://www.youtube.com/watch?v=S5JwBHUgZss&t=1880s), and any data leaving the building must be encrypted. Meta's ScaleAcross paper also mentions deep buffer switches. A deep buffer router chip with line-rate encryption sounds like a good fit for that job. That's my own connection, not something Broadcom claims, so I'll keep researching it.


## Wrapping Up

I learned a lot putting this post together. AI networks use the same L3 CLOS design I'm used to, but everything is pushed harder. Fewer tiers to save optics and power. Optics moving into the switch package. And ECMP, the thing that just worked for years, needs a lot of help when there are only a handful of huge flows.

What I'm still unsure about is how SONiC and FBOSS expose features like DLB and packet trimming. In my next posts, I want to go through congestion control (PFC and DCQCN), and the Meta ScaleAcross paper I mentioned in part two.

_References:_
* _[Arista Networking for AI: The Ethernet Backplane](https://www.youtube.com/watch?v=S5JwBHUgZss) - Tom Emmons, Arista_
* _[Keynote: Networking for AI and HPC, and Ultra Ethernet](https://www.youtube.com/watch?v=0roIi1pscts) - Hugh Holbrook, Arista, NANOG_
* _[RDMA over Ethernet for Distributed AI Training at Meta Scale](https://www.youtube.com/watch?v=oDBMv_5rbQg) - Adi Gangidi, Meta, SIGCOMM 2024_
* _[HN844: Multipath Reliable Connection (MRC)](https://www.youtube.com/watch?v=AQhoTd9rf60) - Packet Pushers_
* _[Reducing Job Completion Time in AI/ML Clusters with Broadcom DNX](https://www.youtube.com/watch?v=XLz2_dOw1U0) - Tech Field Day_
* _[Gilad Shainer, NVIDIA: Scale Up, Scale Out & The Future of AI Networks](https://www.youtube.com/watch?v=3MplvKTuwio) - theCUBE_
* _[Networking for AI: Why Every Network Engineer Should Pay Attention in 2026](https://www.youtube.com/watch?v=mkUP_iQNj2s) - The Art of Network Engineering_
* _[RFC 7938: Use of BGP for Routing in Large-Scale Data Centers](https://datatracker.ietf.org/doc/html/rfc7938)_
* _[RFC 2992: Analysis of an Equal-Cost Multi-Path Algorithm](https://datatracker.ietf.org/doc/html/rfc2992)_
* _[OCP Summit 2025: The open future of networking hardware for AI](https://engineering.fb.com/2025/10/13/data-infrastructure/ocp-summit-2025-the-open-future-of-networking-hardware-for-ai/) - Meta_
* _[Ethernet Standards for Scale-Up AI: An Overview of ESUN, SUE, and UALink](https://www.synopsys.com/articles/ethernet-standards-scale-up-ai.html) - Synopsys_
