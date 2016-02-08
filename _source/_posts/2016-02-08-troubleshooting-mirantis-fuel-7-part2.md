---
title: "Troubleshooting Mirantis Fuel: Problems Creating an APT Mirror"
tags: ['mirantis', 'openstack', 'fuel', 'troubleshooting', 'vagrant']
---

In [Part 1 of Troubleshooting Mirantis Fuel]({% post_url 2016-02-08-troubleshooting-mirantis-fuel-7-part1 %}), it was discovered that
OpenStack installation failed  because the nodes could not reach
the internet. To remedy this, an APT mirror was setup using the ``fuel
create-mirror`` command.

When ``fuel-createmirror`` was executed, it failed. The error message was:

```
* INFO: Resolving dependencies for partial mirror
* FATAL: Cannot calculate list of dependencies
```

An internet search was done to understand how to enable [Fuel
createmirror debugs](https://irclog.perlgeek.de/fuel-dev/2015-09-17).

On the Fuel master node, in  `/opt/fuel-createmirror-7.0/config/`, the
`DEBUG` flag in `ubuntu.cfg` and `mos-ubuntu.cfg` was changed to `yes`.

Then ``sudo fuel-createmirror`` was run again. The true source of the error
appeared.

```
 * INFO: Resolving dependencies for partial mirror
Fetching
'//dists/trusty-updates/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64//initrd.gz'
to
'/var/www/nailgun/ubuntu-full//dists/trusty-updates/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64/'
with params ''...OK
 * DEBUG: Detected debian-installer kernel version: 3.13.0-67-generic
Unable to find image 'ubuntu:latest' locally
Pulling repository ubuntu
time="2016-02-08T14:54:14Z" level="fatal" msg="Could not reach any registry
endpoint"
Error: No such image or container: fuel-createmirror
Could not get docker ID for container fuel-createmirror. Is it running?
Could not get docker ID for fuel-createmirror. Is it running?
 * FATAL: Cannot calculate list of dependencies
 * FATAL: Creation of Ubuntu mirror FAILED, check logs at /var/log/mirror-sync
```

`fuel-createmirror` was trying to install the `ubuntu:latest` docker container.
It fails to pull this container.  [fuel-createmirror
bug](https://bugs.launchpad.net/fuel/+bug/1528498)

The fix is to apply the workaround which was integrated in the vagrant
provisioning script.

```
wget http://mirror.fuel-infra.org/docker/ubuntu.trusty.tar.xz -O /tmp/ubuntu.trusty.tar.xz
sudo docker load -i /tmp/ubuntu.trusty.tar.xz
sudo fuel-creatmirror
```

The Openstack Environment was reset via the Fuel GUI, and the install repeated. There is a _Reset
Environment_ button on the homepage of the Openstack environment.

