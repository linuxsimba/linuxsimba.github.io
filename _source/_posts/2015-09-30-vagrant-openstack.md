---
title: Vagrant Openstack Ansible Deployment
tags: ['vagrant', 'openstack']

---

Finally getting around to working on the [proposed blueprint for the openstack
ansible
deployment]('https://blueprints.launchpad.net/openstack-ansible/+spec/deploy-with-vagrant') found on stackforge.

I decided to settle on learning Openstack using the rackspace private cloud
deployment because they use the LinuxBridge agent by default. Really struggle a
lot with OpenVswitch. So learning core Openstack concepts, especially on the
networking side using the LinuxBridge agent has saved me a lot of time.

I have been playing around with a proposed topology. Thinking of settling on
this one.
<img src='/vagrant-osad.svg'/>


Currently working on understanding the following scenarios, before writing my
first blueprint draft.

1. Tenant separation using VXLAN and VLANs
2. Understanding l2population
3. How to route VM traffic out to the internet. Maybe a little understanding on
security groups, and how this looks like in Iptables
4. Should a 2nd compute node be included by default?
5. How hard is it to replicate this topology using VirtualBox? Currently
implementating is using libvirt

The first draft will mainly some of the ideas around how to use this setup to
learn Openstack concepts well. Perhaps write some blog posts around certain
scenarios, clearly showing how it works.

The [Openstack Ansible Deployment by
Rackspace]('https://github.com/openstack/openstack-ansible'), closely follows the latest
release, so it is simple to keep this testbed up to date with the latest
features and developments in Openstack.

One of the more exciting propositions is to plug switches into this environment,
like Arista, Cumulus, Juniper. This can be easily done in libvirt.

It also doesn not take much to move this config into the cloud using
[Ravello]('https://ravellosystems.com')

After the first draft is done, I plan to work on

1. Cinder Setup
2. Swift Setup
3. Ceilometer

Let us see how things go. This is should be fun!
