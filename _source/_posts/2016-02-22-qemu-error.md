---
title: "Openstack - Fails to create VM due to Qemu Error"
tags: ['openstack', 'qemu', 'troubleshooting']
---

A VM failed to be created in the Openstack environment. It caused a lot of head
scratching for about 30 minutes.

###/var/log/nova/nova.log
```
ERROR nova.compute.manager [instance: eefd6cc2-1efa-4417-b1b5-aa7dfb8d896a] ProcessExecutionError: Unexpected error while running command.
ERROR nova.compute.manager [instance: eefd6cc2-1efa-4417-b1b5-aa7dfb8d896a] Command: qemu-img convert -O raw /var/lib/nova/instances/_base/074cfc7a90d0003439a255eaa493994c492515ab.part /var/lib/nova/instances/_base/074cfc7a90d0003439a255eaa493994c492515ab.converted -f qcow2
ERROR nova.compute.manager [instance: eefd6cc2-1efa-4417-b1b5-aa7dfb8d896a] Exit code: 1
ERROR nova.compute.manager [instance: eefd6cc2-1efa-4417-b1b5-aa7dfb8d896a] Stdout: u''
ERROR nova.compute.manager [instance: eefd6cc2-1efa-4417-b1b5-aa7dfb8d896a] Stderr: u'qemu-img: error while reading sector 2332672: Input/output error\n'

```
After some searches on the web, I found [a post](https://bugs.launchpad.net/nova/+bug/1303802) that explains what this error
means.

Verification of the problem was easy - using `qemu-img check`

```
$ qemu-img check ostinato-dev-debian.qcow2

18060/29398 = 61.43% allocated, 93.36% fragmented, 92.32% compressed clusters
Image end offset: 487915520
root@server1:/var/lib/lxc/stackserver_utility_container-592dbeee/rootfs/root#
qemu-img check ostinato-dev-debian.qcow2
Warning: cluster offset=0x1d200000 is after the end of the image file, can't
properly check refcounts.
Warning: cluster offset=0x1d220000 is after the end of the image file, can't
properly check refcounts.
Warning: cluster offset=0x1d230000 is after the end of the image file, can't
properly check refcounts.
Warning: cluster offset=0x1d310000 is after the end of the image file, can't
properly check refcounts.
Warning: cluster offset=0x1d320000 is after the end of the image file, can't
properly check refcounts.
Warning: cluster offset=0x1d330000 is after the end of the image file, can't
properly check refcounts.
Warning: cluster offset=0x1d340000 is after the end of the image file, can't
properly check refcounts.
Warning: cluster offset=0x1d350000 is after the end of the image file, can't
properly check refcounts.
Warning: cluster offset=0x1d360000 is after the end of the image file, can't
properly check refcounts.
Leaked cluster 3987 refcount=24 reference=15
ERROR OFLAG_COPIED data cluster: l2_entry=800000001d200000 refcount=0
ERROR OFLAG_COPIED data cluster: l2_entry=800000001d220000 refcount=0
ERROR OFLAG_COPIED data cluster: l2_entry=800000001d230000 refcount=0
ERROR OFLAG_COPIED data cluster: l2_entry=800000001d310000 refcount=0
ERROR OFLAG_COPIED data cluster: l2_entry=800000001d320000 refcount=0
ERROR OFLAG_COPIED data cluster: l2_entry=800000001d330000 refcount=0
ERROR OFLAG_COPIED data cluster: l2_entry=800000001d340000 refcount=0
ERROR OFLAG_COPIED data cluster: l2_entry=800000001d350000 refcount=0
ERROR OFLAG_COPIED data cluster: l2_entry=800000001d360000 refcount=0

9 errors were found on the image.
Data may be corrupted, or further writes to the image may corrupt it.

1 leaked clusters were found on the image.
This means waste of disk space, but no harm to data.

9 internal errors have occurred during the check.
18095/29451 = 61.44% allocated, 93.24% fragmented, 92.22% compressed clusters
Image end offset: 488636416

```

The fix was to rebuild the image, and check the new image, before updating the
[Openstack Glance](http://docs.openstack.org/developer/glance/) image
repository.

```
$ pip install disk-image-builder (openstack image builder, if not done already)
$ export DIB_DEV_USER_PWDLESS_SUDO=Yes
$ export DIB_DEV_USER_PASSWORD=linuxsimba
$ disk-image-create debian vm devuser -p ostinato -o ostinato-dev-debian.qcow2
$ qemu-img check ostinato-dev-debian.qcow2

No errors were found on the image.
18094/29451 = 61.44% allocated, 93.30% fragmented, 92.27% compressed clusters
Image end offset: 488570880
```
