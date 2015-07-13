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

### Using the RVM ruby, install all the plugin build dependencies

Confirmed I am running the RVM ruby version, not the system version.

```
$ cd vagrant-libvirt
$ rvm list
$ bundle install
```

### build and install the plugin

Notice that the ``vagrant plugin`` points to the vagrant executabled installed
via ``apt-get`` or ``dpkg``


```
$ bundle exec rake build
$ /usr/bin/vagrant plugin install pkg/vagrant-libvirt-0.0.32.gem

```

Vagrant plugin status will say the plugin installed is _version constrained_. So
this way you can tell the plugin didn not come from the main rubygem repository.

```
$ /usr/bin/vagrant plugin list

pry (0.10.1)
pry-byebug (3.1.0)
rb-readline (0.5.3)
vagrant-libvirt (0.0.30)
  - Version Constraint: 0.0.30
vagrant-lxc (1.1.0)
vagrant-mutate (1.0.0)
vagrant-share (1.1.3, system)
```

