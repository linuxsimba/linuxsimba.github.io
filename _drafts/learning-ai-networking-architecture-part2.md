---
title: "Learning Neural Network Infrastructure  - Part 2"
tags: ["ai", "networking", "roce", "ethernet", "gpu"]
---


This is part 2 of  my series documenting my journey learning about neural network (AI) infrastructure. In [part one]({% post_url 2026-10-08-learning-ai-networking-architecture-part1 %}) I went through my understanding of the history of distributed computing architecture for AI workloads.

In this blog post, I dig into the core concepts that define a RoCEv2 network for AI workloads, covering the terms I came across and the design decisions behind them. My case study is Meta's SIGCOMM 2024 presentation, [RDMA over Ethernet for Distributed AI Training at Meta Scale](https://www.youtube.com/watch?v=wLW3UzUw5rY).


## Core Fabric Design: The Split

For AI workloads, generally require a losseless, non-blocking network. Meta built a network separate from their data and storage traffic just for this GPU-to-GPU traffic. AI training, which I believe drove the first large-scale AI networks, has little tolerance for tail latency at the synchronization barrier. When GPUs exchange their gradients, the information that tells each GPU how to adjust the model's weights, a single delayed GPU holds up the next training step for every other GPU. They sit idle, wasting both time and the money spent on power.

With this split, came the terms frontend network and backend network, and backend networks were further divided into scale-up, scale-out and scale-across. I think frontend and backend, at least, came from the storage world, but I couldn't find a reference showing where the networking industry first adopted these terms.

![Front-end vs back-end networks](/images/frontend-vs-backend-networks.svg)


Here is a breakdown of what these networks do. 

* **Frontend network**: Handles data ingestion, host management, storage checkpoints, and job scheduling over usually using lower bandwidth switches then those on the backend network, completely isolated from GPU synchronization traffic. These networks can be lossy.
* **Backend network**: Dedicated low-latency RDMA over Converged Ethernet (RoCE) fabric built strictly for GPU-to-GPU synchronization and high-bandwidth collective communication
    * _Scale Up_: Ultra-high-bandwidth intra-node interconnect like NVLink, connecting GPUs within a single chassis tray for high-speed tensor sharding and model parallelism
    * _Scale Out_: Inter-node fabric connecting multiple server racks into an AI Zone into a non-blocking Clos topology using RoCEv2 for data parallel collectives
    * _Scale Across_: Multi-zone and inter-cluster network extending beyond individual AI Zones via top-tier aggregation switches (ATSWs) to scale jobs across tens of thousands of GPUs

So I asked myself, why have a scale-up network and a scale-out network? Why can't the scale-up and scale-out networks be collapsed into a single link? Well, Broadcom is moving in that direction by running scale-up over Ethernet, as described in [their SUE Framework announcement in 2025](https://www.broadcom.com/company/news/articles/ai-infrastructure/scale-up-is-simple-ethernet-makes-it-smarter), and I'd like to dig into this in a future blog post.


For now, the two networks are treated as separate infrastructures leveraging different technology.

### AI Workloads: Training vs Inteference

First let's really simplify what a model looks like. First time I heard of a LLM I kept hearing about weights, gradients, tensors, embeddings. So many terms. My head was spinning. 

I'm a simple math guy. I get basic matrix math and vectors. This explanation made the most sense to me which explains an AI model in terms of a bunch of tables. 

* *Entry*: Embedding. Turns input tokens into vectors. Other input types (modalities) like audio or images go through their own encoder but its data is also converted to vectors.

* *Middle*: Transformer layers. Dozens of stacked layers, each with attention (mixes in context from the rest of the input) and feed-forward (transforms what attention gathered).
* *Exit*: Output head. Turns the final vector into a probability for every token in the vocabulary, and the next token is picked from those.

Training is teaching the model. You feed it huge piles of data, check how wrong it is and nudge its weights, over and over, for weeks or months across thousands of GPUs.

Inference is putting the trained model to work. The weights are frozen, nothing new is learned, and it just answers requests, like a router forwarding off a converged routing table.

#### What the scale up network manages

*Training*: When training an AI Model it runs through a series of calculations called activations and these activation calculations are restricted to the scale up network because of the chattiness and speed required.


*Inference*: 

With training there is step that is done within the GPUs in a chassis. Steps like tensor sharing or model parallism. With inference 


### What the scale out network manages

Training: When training an AI Model, there is a step where the GPUs in the training run all have to exchange what they have learnt at that particular stage. AI researchers call them gradients and these gradients affect the weights in the model. This stage called the synchronization barrier is when GPUs starting with the first GPU called rank 0 up to rank N each calculate their gradient and then pass that along to the next GPU. If any GPU is slow or doesn't answer this slows down or halts the training run. This delay is called tail latency and its what network engineers do their darnest to reduce.

Inference:

With training, there is step where the GPUs need to compare their results and exchange data about their results. They call it ???. During this step in a ring fashion data is shared and calculated from one GPU to another. It is critical in this step to 

I'm still research scale-across so I will update this blog post once I fully understand the core concepts.

Model parallelism is splitting one model across multiple GPUs because it is too big to fit in a single GPU's memory. A large language model can have hundreds of gigabytes of weights (the numbers the model learned), while one GPU holds about 80–192 GB. So the model is carved up: either different layers live on different GPUs, or each layer's math is sliced so that several GPUs each compute part of it. The catch is that the GPUs must exchange intermediate results at nearly every layer, many times per training step, and every GPU waits on the others before moving on. Think of it like a modular chassis switch: the line cards and fabric modules together act as one device, and the backplane between them has to be extremely fast and low latency. You would never stretch that backplane across a data center. That is the scale-up network: NVLink inside the server or rack, with roughly 900 GB/s per GPU on an H100.

Data parallelism is running many complete copies of the model, each training on a different slice of the data. Every copy processes its own batch, works out how its weights should be corrected, and then all copies exchange and average those corrections (an operation called all-reduce) so that every copy stays identical before the next step begins. It works much like routers in an OSPF area: each router runs SPF independently on its own view, but the LSDBs must be synchronized before the network can converge. This traffic happens once per step instead of once per layer, so it can tolerate more latency, but it arrives as huge, synchronized bursts from thousands of GPUs at the same moment, which is a worst-case incast pattern. That is the scale-out network: RoCEv2 over a Clos fabric, typically one 400G NIC per GPU, or about 50 GB/s.

So the two networks can't be collapsed because their requirements pull in opposite directions. Model parallelism needs roughly 18x more bandwidth per GPU at sub-microsecond latency, which today is only practical over short copper inside a rack. Data parallelism needs to reach tens of thousands of GPUs across a building, which is what Ethernet and Clos designs are good at.



I scratched my head for a while wondering how to best understand what model parallelism (scale up) is, vs data parallelism (scale out) and the best way I can think of it is consider each chassis of GPUs as a commercial kitchen. Each kitchen is charged with building a a set of recipes from a recipe book that they eat have a copy of. Each kitchen cooks a their respective recipes (model parallism) and then when its done serving it to its respective guests, it exchanges the feedback from the guests to each kitchen. So kitchen A says, the duck needs a little more salt and kitchen B says the chicken needs to be broiled a little more. This is the data parallism phase. Now both kitchen the adjustments to the recipes and they continue going through the next set of recipes and continue this process.
