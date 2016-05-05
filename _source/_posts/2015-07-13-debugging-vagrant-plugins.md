---
title: Debugging Vagrant plugins
tags: ['vagrant', 'development']
---


Recently posted a [Pull Request to the
vagrant-libvirt](https://github.com/vagrant-libvirt/vagrant-libvirt/pull/413) project.

I have rvm installed, so I think during that install, I have most of the
dependencies for doing ruby development.

While debugging a vagrant plugin
I run ``rvm use system`` from the terminal since ``/usr/bin/vagrant`` needs to run and I have
vagrant gem installed in the rvm ruby gem folder for vagrant plugin building.

To create the patch, I did the following to troubleshooting

### install [pry-byebug](https://github.com/deivid-rodriguez/pry-byebug) into the vagrant gem directory
This is the ruby debugger recommended by a couple of sites for ruby2+ versions

```
vagrant plugin install pry-byebug
```


### insert breakpoints where needed
Open the vagrant plugin file and add ``require pry`` at the top and
``binding.pry`` at the line to start the debugger.

Example
#### _/home/stanley/.vagrant.d/gems/gems/vagrant-libvirt-0.0.30/lib/vagrant-libvirt/action/create_network_interfaces.rb_

```
3 require 'vagrant/util/scoped_hash_override'
4 require 'pry-byebug'
...
....
......
39           # Vagrant gives you adapter 0 by default
40           # Assign interfaces to slots.
41           configured_networks(env, @logger).each do |options|
42             binding.pry

```

### run vagrant normally, and it will break at the point requested

For some reason, I cannot step into ruby block code. Still something to figure
out.

```
$ vagrant up
Bringing machine 'test1' up with 'libvirt' provider...
==> test1: Creating image (snapshot of base box volume).
==> test1: Creating domain with the following settings...
==> test1:  -- Name:              vagrant_testing_test1
==> test1:  -- Domain type:       kvm
==> test1:  -- Cpus:              1
==> test1:  -- Memory:            128M
==> test1:  -- Base box:          trusty64_2
==> test1:  -- Kernel:
...
....
==> test1: Creating shared folders metadata...

From: /home/stanley/.vagrant.d/gems/gems/vagrant-libvirt-0.0.30/lib/vagrant-libvirt/action/create_network_interfaces.rb @ line 44 VagrantPlugins::ProviderLibvirt::Action::CreateNetworkInterfaces#call:

    39:           # Vagrant gives you adapter 0 by default
    40:           # Assign interfaces to slots.
    41:           configured_networks(env, @logger).each do |options|
    42:             binding.pry
    43:             # dont need to create interface for this type
 => 44:             next if options[:iface_type] == :forwarded_port
    45:
    46:             # TODO fill first ifaces with adapter option specified.
    47:             if options[:adapter]
    48:               if adapters[options[:adapter]]
    49:                 raise Errors::InterfaceSlotNotAvailable

```


### copy the changed file to my git fork of the plugin
I copied the changed ruby file to my git fork of the plugin and remove
all my debugs.



Probably not the recommended way to test and modify a plugin, but it works for
me :)

