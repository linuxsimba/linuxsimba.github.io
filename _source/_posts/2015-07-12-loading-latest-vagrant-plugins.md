---
title: Loading Latest Vagrant Plugins From Git
tags: ['vagrant', 'development']
---

I am using Ubuntu 14.04 and have [RVM](http://rvm.io) with Ruby 2.2 installed
I don not like to pollute my system ruby version with development work.  So I
use [RVM](http://rvm.io).

### clone the vagrant plugin git project

```
$ git clone https://github.com/pradels/vagrant-libvirt

```

### Build the Gem

Seems like any GEM version will do. Does not seem to need a newer ruby
installed.

```
$ gem build vagrant-libvirt.gemspec

$ vagrant plugin install vagrant-libvirt-0.0.31.gem
```


Vagrant plugin status will say the plugin installed is _version constrained_. So
this way you can tell the plugin didn not come from the main rubygem repository.

```
$ /usr/bin/vagrant plugin list

pry (0.10.1)
pry-byebug (3.1.0)
rb-readline (0.5.3)
vagrant-libvirt (0.0.31)
  - Version Constraint: 0.0.31
vagrant-lxc (1.1.0)
vagrant-mutate (1.0.0)
vagrant-share (1.1.3, system)
```

