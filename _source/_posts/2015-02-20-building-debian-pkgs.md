---
title: Learning How To Build Debian Packages From Source
---

I want to build a really cool app called
[sflowtool](http://www.inmon.com/technology/sflowTools.php) into source debian
package that I can then compile for use on a [Cumulus Switch](http://cumulusnetworks.com) or
Ubuntu server, or Rasperry PI.

There is too much information about how to perform debian packaging, including the packaging
guide, which is long and complicated. I figured, I better blog about something
that works for me, so next year, I can just reference my own site!

## Option 1: Use checkinstall

[checkinstall](https://help.ubuntu.com/community/CheckInstall) is cool. Easiest
tool I found to quickly build a deb. 

## Option 2: dh_make and dpkg-buildpackage

Using dh_make and dpkg-buildpackage provides 
some more flexibility, in areas where I want to provide a simple patch or
change the compile options in `debian/rules` file.
 
These are the basic steps to go through using dh_make and dpkg-buildpackage.

### Install necessary apps
```
$ sudo apt-get install dpkg-dev dh-make
```

### untar source archive and run dh_make
```
$ tar xvfz /vagrant/sflowtool-3.34.tar.gz
$ cd sflowtool-3.34
$ dh_make --native
Type of package: single binary, indep binary, multiple binary, library, kernel
module, kernel patch?
 [s/i/m/l/k/n] s

Maintainer name  : unknown
Email-Address    : vagrant@linuxsimba.local 
Date             : Thu, 18 Feb 2015 01:31:16 +0000
Package Name     : sflowtool
Version          : 3.34
License          : gpl3
Type of Package  : Single
Hit <enter> to confirm: 
Done. Please edit the files in the debian/ subdirectory now. sflowtool
uses a configure script, so you probably don't have to edit the Makefiles.
```

## modify the debian/control file
List at least 2 sections in this file.
One section starting with `Source` will define the control parameters for the
source deb. 

The 2nd section starting with a **linebreak** and then the word `Package:` will
cover what is defined for the binary package.

{% gist e229f250d31204d70a2c %}

### Modify the debian/changelog file

When running `dpkg-buildpackage I use the `-uc` and `-us` to ignore building with a gpg key
{% gist 46fd07acf09e06751d2c %}

## Modify the debian/docs file
Lists the files that go into the documentation
folder listed in the deb
{% gist 38ce8a70cb1686b3b7d7 %}

### Run dpkg-buildpackage 

I ignore signing any files when doing this.
by running `dpkg-buildpackage -us -uc`
Because the output is so long, the complete output of a
`dpkg-buildpackage` run can be found on a [gist I created](https://gist.github.com/skamithi/73bb37d70a1e86872f97)

## Option 3: git-buildpackage
Its on my TODO list to understand the real power behind this
`dpkg-buildpackage` wrapper.

## What I am using for now

I think for now, I'll be playing with `git-buildpackage`. My working example
will continue to be the sflowtool package. 

To build the sflowtool on a particular platform, [git clone the sflowtool repo
I maintain](http://github.com/skamithi/sflowtool.git) and run `git-buildpackage`
## References

[Packaging New Ubuntu Software](http://packaging.ubuntu.com/html/packaging-new-software.html)

[Building a Simple Debian Package](https://faceted.wordpress.com/2011/05/18/howto-build-a-trivial-debian-package-with-dh_make/)

[Keysigning](https://wiki.debian.org/Keysigning)
