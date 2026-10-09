---
title: "Learning Neural Network Infrastructure  - Part 2"
tags: ["ai", "networking", "roce", "ethernet", "gpu"]
---


This is part 2 of  my series documenting my journey learning about neural network (AI) infrastructure. In [part one]({% post_url 2026-10-08-learning-ai-networking-architecture-part1 %}) I went through my understanding of the history of distributed computing architecture for AI workloads.

In this blog post, I dig into the core concepts that define a RoCEv2 network for AI workloads, covering the terms I came across and the design decisions behind them. My case study is Meta's SIGCOMM 2024 presentation, [RDMA over Ethernet for Distributed AI Training at Meta Scale](https://www.youtube.com/watch?v=wLW3UzUw5rY).


## Core Fabric Design: The Split

For AI workloads, due to the bursty nature of AI data parallelism traffic and its requirement to be losseless, it was decided that GPU to GPU traffic be put a separate network. This data parallelism workflow is very sensitive to data loss. If one GPU is "slow", all GPUs in that operation pause until that GPU is done resulting in idle time. And GPU idle time is a loss financially.

The terms frontend and backend network was introduced, and backend networks where further broken down in to scale-up, scale-out and scale-across networks. I think these terms, at least frontend and backend originated from the storage world. I couldn't find a specific reference showing the origin of the adoption of these terms.

![Front-end vs back-end networks](/images/frontend-vs-backend-networks.svg)


Here is a breakdown of what these networks do. 

* Frontend network: Handles data ingestion, host management, storage checkpoints, and job scheduling over standard Ethernet (100G/200G), completely isolated from GPU synchronization traffic. These networks can be lossy. To save on cost, these networks typically do not run the fastest switches.
* Backend network: Dedicated low-latency RDMA over Converged Ethernet (RoCE) fabric built strictly for GPU-to-GPU synchronization and high-bandwidth collective communication
    * Scale Up: Ultra-high-bandwidth intra-node interconnect (NVLink/NVSwitch or OAM fabric) linking GPUs within a single chassis tray for high-speed tensor sharing and model parallelism
    * Scale Out: Inter-node fabric connecting multiple server racks into an AI Zone into a non-blocking Clos topology using RCOEv2 for data parallel collectives
    * Scale Across: Multi-zone and inter-cluster network extending beyond individual AI Zones via top-tier aggregation switches (ATSWs) to scale jobs across tens of thousands of GPUs

### Training vs Inference

So I asked myself, why have a scale-up network and a scale-out network. Why can't this network be collapsed. It requires some understand of AI workloads.

The most common workloads are training and inference.

Training is..

Inference is..

#### What the scale up network manages
With training there is step that is done within the GPUs in a chassis. Steps like tensor sharing or model parallism. With inference 


### What the scale out network manages
With training, there is step where the GPUs need to compare their results and exchange data about their results. They call it ???. During this step in a ring fashion data is shared and calculated from one GPU to another. It is critical in this step to 

I'm still research scale-across so I will update this blog post once I fully understand the core concepts.

Model parallelism is splitting one model across multiple GPUs because it is too big to fit in a single GPU's memory. A large language model can have hundreds of gigabytes of weights (the numbers the model learned), while one GPU holds about 80–192 GB. So the model is carved up: either different layers live on different GPUs, or each layer's math is sliced so that several GPUs each compute part of it. The catch is that the GPUs must exchange intermediate results at nearly every layer, many times per training step, and every GPU waits on the others before moving on. Think of it like a modular chassis switch: the line cards and fabric modules together act as one device, and the backplane between them has to be extremely fast and low latency. You would never stretch that backplane across a data center. That is the scale-up network: NVLink inside the server or rack, with roughly 900 GB/s per GPU on an H100.

Data parallelism is running many complete copies of the model, each training on a different slice of the data. Every copy processes its own batch, works out how its weights should be corrected, and then all copies exchange and average those corrections (an operation called all-reduce) so that every copy stays identical before the next step begins. It works much like routers in an OSPF area: each router runs SPF independently on its own view, but the LSDBs must be synchronized before the network can converge. This traffic happens once per step instead of once per layer, so it can tolerate more latency, but it arrives as huge, synchronized bursts from thousands of GPUs at the same moment, which is a worst-case incast pattern. That is the scale-out network: RoCEv2 over a Clos fabric, typically one 400G NIC per GPU, or about 50 GB/s.

So the two networks can't be collapsed because their requirements pull in opposite directions. Model parallelism needs roughly 18x more bandwidth per GPU at sub-microsecond latency, which today is only practical over short copper inside a rack. Data parallelism needs to reach tens of thousands of GPUs across a building, which is what Ethernet and Clos designs are good at.



I scratched my head for a while wondering how to best understand what model parallelism (scale up) is, vs data parallelism (scale out) and the best way I can think of it is consider each chassis of GPUs as a commercial kitchen. Each kitchen is charged with building a a set of recipes from a recipe book that they eat have a copy of. Each kitchen cooks a their respective recipes (model parallism) and then when its done serving it to its respective guests, it exchanges the feedback from the guests to each kitchen. So kitchen A says, the duck needs a little more salt and kitchen B says the chicken needs to be broiled a little more. This is the data parallism phase. Now both kitchen the adjustments to the recipes and they continue going through the next set of recipes and continue this process.
