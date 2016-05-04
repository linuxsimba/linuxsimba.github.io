---
title: Libvirt-vagrant fails to bundle install
tags: ['vagrant', 'libvirt', 'ruby']
---

Interesting error message when running ``bundle install`` on the [libvirt-vagrant
plugin]('https://github.com/vagrant-libvirt/vagrant-libvirt/')

```
Gem::Ext::BuildError: ERROR: Failed to build gem native extension.

    /home/osad/.rvm/rubies/ruby-2.1.5/bin/ruby -r
./siteconf20150722-2961-ziutum.rb extconf.rb
*** extconf.rb failed ***
Could not create Makefile due to some reason, probably lack of necessary
libraries and/or headers.  Check the mkmf.log file for more details.  You may
need configuration options.

Provided configuration options:
  --with-opt-dir
  --without-opt-dir
  --with-opt-include
  --without-opt-include=${opt-dir}/include
  --with-opt-lib
  --without-opt-lib=${opt-dir}/lib
  --with-make-prog
  --without-make-prog
  --srcdir=.
  --curdir
  --ruby=/home/osad/.rvm/rubies/ruby-2.1.5/bin/ruby
  --with-libvirt-include
  --without-libvirt-include
  --with-libvirt-lib
  --without-libvirt-lib
  --with-libvirt-config
  --without-libvirt-config
  --with-pkg-config
  --without-pkg-config
extconf.rb:73:in `<main>': libvirt library not found in default locations
(RuntimeError)

```

Simple fix


```
$ sudo apt-get install libvirt-dev
```


Wish it just said, could not find libvirt development libraries..

Probably should just issue a PR for the ruby-libvirt library. I will add that to
my todo list



