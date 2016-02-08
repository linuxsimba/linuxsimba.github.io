---
title: "Troubleshooting Mirantis Fuel: Problems Creating an APT Mirror"
tags: ['mirantis', 'openstack', 'fuel', 'troubleshooting', 'vagrant']
---

In [Part 1 of Troubleshooting Mirantis Fuel]({% post_url 2016-02-08-troubleshooting-mirantis-fuel-7-part1 %})
it was discovered that OpenStack apps
failed to be installed on the respective nodes because the nodes could not reach
the internet. To remedy this an APT mirror would be setup using the ``fuel
create-mirror`` command.

When ``fuel-createmirror was executed, it failed. The error message was:

```
* INFO: Resolving dependencies for partial mirror
* FATAL: Cannot calculate list of dependencies
```

Not a helpful message so searched the internet to find out how to turn on [Fuel
createmirror debugs](https://irclog.perlgeek.de/fuel-dev/2015-09-17)

On the Fuel master node, in  `/opt/fuel-createmirror-7.0/config/` change the
`DEBUG` flag in `ubuntu.cfg` and `mos-ubuntu.cfg` to `yes`.

After doing that and executing ``sudo fuel-createmirror -U`` again, the true source of the error is revealed

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

`fuel-createmirror` is trying to install the `ubuntu:latest` docker container.
It fails to pull this container. Why? Apparently its a [fuel-createmirror
bug](https://bugs.launchpad.net/fuel/+bug/1528498)

The fix to to apply the workaround which was integrated in the vagrant
provisioning script.

```
wget http://mirror.fuel-infra.org/docker/ubuntu.trusty.tar.xz -O /tmp/ubuntu.trusty.tar.xz
sudo docker load -i /tmp/ubuntu.trusty.tar.xz
sudo fuel-creatmirror
```

Reset the Openstack Environment via the Fuel GUI. But still encountered a problem. See Part 3 of Mirantis Fuel Troubleshooting.

