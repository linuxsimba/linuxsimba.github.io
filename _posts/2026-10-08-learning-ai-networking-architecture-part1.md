---
title: "Learning Neural Network Infrastructure - Part 1"
tags: ["ai", "networking", "infiniband", "ethernet", "gpu"]
---


I have been out of the data center world for a few years, dabbling in custom app and SaaS development, deployment and support. Today, I'm teaching myself the ins and outs of machine learning and have an opportunity to re-enter computer networking from an AI perspective. I'm learning how to use AI to solve problems I encounter personally and in my career, and this blog series follows my journey learning the infrastructure used to train and run neural networks. It covers what I’ve learned about its history, and especially why the neural network infrastructure looks the way it does today.


## Part 1 - Neural Network Infrastructure Evolution


### In the beginning... InfiniBand's dominance
The earliest reference I found for networking in neural networks was a [paper from 2012 by Dr. Hinton and his team](https://papers.nips.cc/paper_files/paper/2012/hash/c399862d3b9d6b76c8436e924a68c45b-Abstract.html). A fellow researcher challenged him to see whether his neural network research could win the ImageNet competition and properly categorize pictures of animals. Dr. Hinton's team used a single computer with 2 GPUs, NVIDIA GTX 580s. This was the first evidence I found of splitting a job between GPUs. They divided the neural network between the two cards.

In 2013, Coates, Huval and others wrote a paper called [Deep Learning with COTS HPC systems](https://proceedings.mlr.press/v28/coates13.html) where they stated that using an InfiniBand switch to connect servers with GPUs was a better solution for "copying parameters or gradients" between other servers with GPUs than using "commodity Ethernet". The paper said using Ethernet was "several orders of magnitude slower".

In 2016, [Iandola described his InfiniBand network](https://www.researchgate.net/publication/332187944_Distributed_deep_neural_network_training_A_measurement_study), indicating to me that by this time, InfiniBand had become the de facto networking standard for connecting GPU servers for AI training.

![2016 infiniband](/images/2016-infiniband-network.png)

*Figure from Iandola (2016), [source paper](https://www.researchgate.net/publication/332187944_Distributed_deep_neural_network_training_A_measurement_study).*


Compared with Ethernet at the time, InfiniBand had Remote Direct Memory Access support, which is the ability to copy data from the NIC directly into the RAM accessible to the GPU. The InfiniBand switches provide lossless connectivity to the remote NIC.

![GPU to NIC data paths](/images/gpu-nic-paths.svg)

AI training and inference are distributed computing workloads. InfiniBand was designed to handle distributed computing problems and proved itself a natural fit for neural network infrastructure. But it had problems, especially at scale.



### "Ethernet is a business model, not a specific technology" - The rise of RoCEv2

I love this quote from Bob Metcalfe, the co-inventor of Ethernet. Ethernet proponents always have a way to fight back whenever champions of a new protocol try to replace Ethernet. 

I suspect that, with the growth of AI, DeepMind's successes with protein folding, the creation of transformers, and LLMs, Ethernet proponents got very concerned about the rise of InfiniBand. Let's see how Ethernet supporters fought back against InfiniBand.

![InfiniBand vs Ethernet fight meme](/images/fight-meme-infiniband-vs-ethernet.jpg)


#### _"If InfiniBand was so good at lossless low-latency networks, why create RDMA over Converged Ethernet (RoCE)?"_

In 2009, David Cohen et al. wrote a paper titled [Remote Direct Memory Access over Converged Enhanced Ethernet Fabric: Evaluating the Options](https://www.researchgate.net/publication/232624574_Remote_Direct_Memory_Access_over_the_Converged_Enhanced_Ethernet_Fabric_Evaluating_the_Options). It states that the industry wants inter-process communication, storage and LAN networking to converge onto a single physical fabric, avoiding the higher capital and operational costs of running a separate unique network for each. The ongoing work on lossless Ethernet (CEE/DCB) affords the opportunity to put RDMA over Ethernet. Prior attempts to add RDMA to the Ethernet world, like iWARP, which requires complex TCP software stacks, failed.

#### _"If RoCE was proposed because of DCB, why was IEEE working on DCB in the first place?"_


Asif Hazarika and Gopi Sirineni in their 2005 presentation [Amendment to 802.1Q: Congestion management](https://www.ieee802.org/1/files/public/docs2005/liaison-hazarika_gopi-congestion-management-par-bkgnd-2-0511.pdf) stated that "To broaden and sustain the Ethernet market, congestion management is a must!" and also mentioned InfiniBand as a threat to Ethernet.

They identified a critical weak point in Ethernet. It's a lossy standard. In order to stay relevant, it had to adapt. Even as early as 2005, the computer industry was realizing that some applications work better in a lossless environment, e.g., financial trading and storage networks. 

By 2011, Data Center Bridging standards were approved, including Priority Flow Control (PFC), a component RDMA over Converged Ethernet depends on.

By 2014, RDMA over Converged Ethernet was in its second version. Microsoft decided to place it into production. Chuanxiong Guo of Microsoft, in his video titled [RDMA over Commodity Ethernet at Scale](https://www.youtube.com/watch?v=QTHSGmPhVEs), went through all the struggles they had using RoCEv2. At the end, he gave no indication that they would change to InfiniBand. They planned to work through the bugs and problems. In a future post, I want to go through each of the problems he identified and see whether these issues are resolved as of 2026.

#### _"Is Ethernet adoption for AI networks growing?"_ 

Yes, commodity Ethernet switching deployments for AI scale-out networks are growing. [Dell'Oro](https://www.delloro.com/news/ethernet-extends-lead-in-ai-scale-out-networks-despite-strong-infiniband-rebound/), an industry analyst firm, indicates that Ethernet is extending its lead in AI scale-out networks. 

Rohan Mehta, a Senior Software Engineer at Microsoft, stated in a [SNIA video titled "Everything you Wanted to know about RDMA but were too proud to ask"](https://www.youtube.com/watch?v=6t041Lr5FCY&t=1s) that InfiniBand doesn't scale well. Deploying InfiniBand involves introducing new Layer 2, 3 and 4 stacks. Ethernet and IP, he said, are ubiquitous.


### What's Next?

Next, I will look at the common switching and server designs neural network infrastructure relies on when commodity Ethernet switches are used. I will focus on data Meta (Facebook) presented at SIGCOMM 2024.
