---
title: "Learning Neural Network Infrastructure - Part 2"
tags: ["ai", "networking", "roce", "ethernet", "gpu"]
---


This is part 2 of my series documenting my journey learning about neural network (AI) infrastructure. In [part one]({% post_url 2026-10-08-learning-ai-networking-architecture-part1 %}), I went through my understanding of the history of distributed computing architecture for AI workloads.

In this blog post, I dig into AI training workflows and which operations of the workflow require networking.


## AI Workloads: Training vs Inference

First, let's really simplify what a model looks like. The first time I heard about an LLM, I kept hearing about weights, gradients, tensors, embeddings. So many terms. My head was spinning. 

I'm a simple math guy. I get basic matrix math and vectors. The following explanation made the most sense to me. It explains an AI model in terms of a bunch of tables. 

* *Entry Tables*: Embedding. Turns input tokens into vectors. Other input types (modalities) like audio or images go through their own encoder, but their data is also converted to vectors.
* *Middle Tables*: Transformer layers. Dozens of stacked layers of weights (floating point numbers), each with attention (weights that let each token mix in context from the rest of the input) and feed-forward (transforms what attention gathered).
* *Exit Tables*: Output head. Turns the final vector into a probability for every token in the vocabulary, and the next token is picked from those.


Training is teaching the model. You feed it huge piles of data, check how wrong it is and nudge its weights, over and over, for weeks or months across thousands of GPUs.

Inference is putting the trained model to work. The weights are frozen, nothing new is learned, and it just answers requests, like a router forwarding off a converged routing table.

## Core Fabric Design: The Split

AI training workloads require a lossless, non-blocking network. 

I think at the beginning of building AI networks at scale, the first need was to manage AI training. AI training has little tolerance for tail latency during the phases where GPUs exchange data amongst themselves. 

Managing GPU-to-GPU traffic is like managing a little baby that needs a lot of attention and tuning, and the industry decided to house this traffic on a separate fabric from config, storage or monitoring traffic. I believe the AI networking industry borrowed the terms frontend and backend network from the storage world and then took them to the next level, further subdividing a backend network into scale-up, scale-out and scale-across fabrics.


![Front-end vs back-end networks](/images/frontend-vs-backend-networks.svg)


This is what I understand so far about the different network or fabric definitions:

* **Frontend network**: Handles data ingestion, host management, storage checkpoints, and job scheduling, usually over lower-bandwidth switches than those on the backend network, completely isolated from GPU synchronization traffic. These networks can be lossy. So from an AI training perspective, downloading model info from storage, Kubernetes configs to start the training runs, or telemetry data for the monitoring systems are examples of traffic on this network.
* **Backend network**: It's a set of networks combined to provide a lossless, non-blocking environment for GPU-to-GPU traffic. 
    * _Scale Up_: Ultra-high-bandwidth intra-node interconnect like NVLink, connecting GPUs within a server or rack (e.g., NVL72). This is the fastest link between GPUs. Unfortunately it is limited and I believe expensive to provision. But according to <blah video>, there is a desire to scale these domains from the current 72 (2026 numbers) to 1024.
    * _Scale Out_: Inter-node lossless, non-blocking fabric. It can use either InfiniBand or RoCEv2. For now, I'm focusing on RoCEv2 networks.
    * _Scale Across_: Multi-zone and inter-cluster network extending beyond individual AI Zones. InfiniBand can be extended with NVIDIA MetroX switches, but from what I've read, Ethernet technologies are more scalable and operationally easier to manage. Technical details about scale-across deployments are hard to find, but see below for what I've found so far.

What was confusing me was what traffic goes across a scale-across network. I finally found someone asking that exact question in a video titled [Arista Networking for AI: The Ethernet Backplane](https://www.youtube.com/watch?v=S5JwBHUgZss&t=264s). Tom Emmons from Arista said yes, GPU-to-GPU traffic does go across it, and Meta has talked publicly about training across locations. But it's only the traffic that can handle the extra latency, usually the data parallel all-reduces. He also said you can't just bring up PyTorch and make it work. It takes a lot of full stack engineering. [Later in the talk](https://www.youtube.com/watch?v=S5JwBHUgZss&t=1847s), he said the network looks a lot like a traditional WAN, with deep buffer switches, encryption on anything leaving the building, and traffic engineering.

So I went looking for what Meta has said about scale-across networks, and I found a May 2026 paper from Meta and Harvard titled [ScaleAcross Explorer: Exploring Communication Optimization for Scale-Across AI Model Training](https://arxiv.org/abs/2605.24326). It confirms what Emmons said. Llama 3 was trained on 16K GPUs in a single building, but Llama 4 was trained on over 100K GPUs spread across multiple buildings. Meta puts data parallelism (FSDP) across the buildings and keeps the chattier tensor and expert parallel traffic inside an AI zone. What I found interesting is that they rely on deep buffer switches and actually turn off congestion control. This paper deserves its own post, so I'll dig into it later.


## AI Training Flow from a network perspective

There are a few ways to train a neural network depending on its size, but I wanted to focus on what I think is the most elegant training flow I came across: Fully Sharded Data Parallel (FSDP) training.

Here is a diagram of what I've figured out so far.

![FSDP training lifecycle](/images/fsdp-training-cycle.jpg)

_References:_
* _[Demystifying NCCL: An In-depth Analysis of GPU Communication Protocols and Algorithms](https://arxiv.org/html/2507.04786v3) - Zhiyi Hu et al._
* _[How Fully Sharded Data Parallel Works](https://www.youtube.com/watch?v=By_O0k102PY&t=775s) - Ahmed Tala_

According to Zhiyi Hu and others, training programs call the NVIDIA Collective Communications Library (NCCL). A collective is a synchronized communication operation where every participating GPU (rank) contributes data and receives a result. For example, reduce-scatter is a collective because it sums the corrections (gradients) from every GPU and hands each GPU one slice of the result. I think I need to create a glossary of AI networking terms because there are so many.

Reduce-scatter and all-gather generate the GPU-to-GPU traffic seen when FSDP runs, but not all of it hits the scale-out network. GPUs in the same server exchange their part over NVLink, and only the part that has to cross servers goes over the scale-out network. I'm still researching what kind of traffic pattern they produce, but my suspicion is that it's bursty, nearly simultaneous if you have thousands of GPUs in the mix, and probably low entropy. That's another common term I've heard in AI networking videos. Low entropy means traffic that consists of a few large, repetitive flows, which is a problem for load balancing. In a future post, I'll go through the articles and information I've found on improving load balancing across RoCEv2 switches, and in another post, the industry's efforts to improve AI traffic congestion management.

I'm not talking about InfiniBand in any of these blog posts, as that's not an area I want to research right now. I'm studying the RoCE protocol, which uses a lot of language and design from InfiniBand, but learning InfiniBand is on my roadmap. I'll probably learn it next year, in 2027.

Anyways, back to AI training flows. What I learned is that certain collectives make up the bulk of the traffic on scale-out networks. NCCL makes this a little smarter by doing some operations over NVLink and only using the scale-out network when necessary.


### Parallelism Terminology

I found several videos and references to tensor parallelism, data parallelism, model parallelism and pipeline parallelism.

I wanted to understand exactly what these mean because, again, it's confusing, especially if you are not an AI researcher. So here is a table describing what each means, how they differ and how each impacts a scale-out network.

| Parallelism | Meaning (short) | Preferred Fabric | Traffic Character | Network Impact |
|-------------|-----------------|------------------|-------------------|----------------|
| **Data Parallelism** | Split the data across GPUs; each holds a (full or sharded) copy of the model and syncs gradients. FSDP is a sharded form of this. | Scale-out (InfiniBand/RoCE); scale-up if multi-GPU node | Large, synchronized, low-entropy elephant flows every iteration | Heavy predictable load on scale-out; tail latency directly slows the job |
| **Tensor Parallelism** | Split individual layers/tensors (e.g. matrix multiplies) across GPUs that work on pieces of the same operation. | Scale-up (NVLink) strongly preferred | Very high bandwidth, low latency, frequent intra-layer exchanges | Stays on NVLink when placed well; spills to scale-out kill performance |
| **Pipeline Parallelism** | Split the model into sequential stages (groups of layers); pass activations between stages. | Point-to-point; scale-up or scale-out depending on placement | Smaller, streaming / micro-batch traffic | Sensitive to latency and jitter; cross-node placement creates scale-out flows |
| **Model Parallelism** | Umbrella term for splitting the model itself (includes tensor and pipeline parallelism). | Depends on subtype | Depends on subtype | Impact is whatever the chosen subtype generates |



Next up, [part three]({% post_url 2026-10-11-learning-ai-networking-architecture-part3 %}), where I go through L3 CLOS topologies, optics, ECMP and why AI training traffic gives it so much trouble.
