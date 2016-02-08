---
title: Using Vagrant-Libvirt to Virtualize A Mirantis OpenStack Deployment
tags:
  - mirantis
  - openstack
---

> **08 Feb 2016**: Currently unable to complete a Mirantis Openstack setup in
this virtual environment. Working through somes issues. Got a [couple of blog
posts](/mirantis.html) documenting what problems encountered so far.

[Mirantis Fuel](https://wiki.openstack.org/wiki/Fuel) is a bare-metal installer
for OpenStack. Mirantis provides a way to virtualize the [setup using
VirtualBox](https://docs.mirantis.com/openstack/fuel/fuel-6.1/virtualbox.html).
Decided to virtualize Mirantis Fuel using
[vagrant-libvirt](https://github.com/pradels/vagrant-libvirt). Using a Vagrant
Box  opens the
door to build virtual setups that include the underlay, like the switches (_Cumulus VX_) and
external routers (_Cisco VM_)

### Download the Mirantis Fuel ISO
Mirantis does not provide a URL for the ISO, so you have to sign up for it on
the [Mirantis Fuel Download
Page](https://software.mirantis.com/openstack-download-form/).

Copy the ISO to the ``$HOME/openstack`` directory. This is where the packer
template is assuming the ISO to be.

### Build the Mirantis Fuel Vagrant Box

* [Install Vagrant-libvirt ]({% post_url 2015-08-11-vagrant-libvirt-install %})

* [Download and install packer](https://www.packer.io/intro/getting-started/setup.html)

* Git clone the packer repo with the Mirantis Fuel packer build script


```
git clone http://github.com/linuxsimba/packer-libvirt-profiles
```

* Assign a temporary directory with at least 30GB of space. Defaults to /tmp. If
/tmp is small then the build process will fail with a space exceeded message.

```
export TMPDIR=$HOME/tmp
```

* Go to the packer build repo and run packer. Wait 14-45 minutes depending on
the speed of your PC.

```
cd packer-libvirt-profiles
packer build packer build mirantis-7-x86_64.json
```

A vagrant libvirt box will be created in the following packer build repo
directory.


<pre><code>
==> qemu (vagrant): Creating Vagrant Box for 'libvirt' provider
    qemu (vagrant): Copying from artifact: packer-mirantis-7-qemu/mirantis-7
    qemu (vagrant): Compressing: Vagrantfile
    qemu (vagrant): Compressing: box.img
    qemu (vagrant): Compressing: metadata.json
Build 'qemu' finished.

==> Builds finished. The artifacts of successful builds are:
--> qemu: 'libvirt' provider box: <strong>builds/mirantis-fuel-7.libvirt.box</strong>
</code></pre>


* Copy the Vagrant Box into the default Vagrant Box location


```
vagrant box add builds/mirantis-fuel-7.libvirt.box --name "mirantis-7"
```


### Start the Topology


<img src='/mirantis-openstack.svg'/>



```
mkdir $HOME/openstack-mirantis
cd $HOME/openstack-mirantis
vagrant init
cp $HOME/git/packer-libvirt-profiles/vagrantfile_examples/Vagrantfile.mirantis Vagrantfile
vagrant up --no-parallel
```


Using the [example
Vagrantfile](http://github.com/linuxsimba/packer-libvirt-profiles/blob/master/vagrantfile_examples/Vagrantfile.mirantis)
the test virtual setup looks the topology shown above.
It has a back-to-back connection between the first server and the 2nd server.

Used a back-to-back connection for simplicity because Mirantis with VLAN
segmentation configures the non-admin NIC as a trunk with VLANS for storage,
management and Openstack projects. In the near future switches will be put
between the servers to develop a more complex network.

The topology takes advantage of the [libvirt PXE boot
feature](https://libvirt.org/formatdomain.html#elementsNICSBoot). So the Server
nodes come up in vagrant but the disks are empty. Vagrant can only halt or start
a PXE enabled Vagrant instance. Use ``virsh`` commands instead for any other
commands.

> Would be interesting to know how PXE booting works with the Vagrant-Virtualbox provider.

Run vagrant with ``no-parallel`` because the Fuel master needs to be up and
running first, to become a PXE and DHCP server for the openstack server nodes.

It will take a while for the Fuel master to load, because it has to install
docker containers. On my Intel I5 server it took about 40 minutes to complete.
About 20 minutes was needed to setup the APT mirror.

A port forward setting is configured in Vagrant, to access the Fuel GUI when
``vagrant up`` has completed.

Go to [http://localhost:8000](http://localhost:8000) to access the Fuel
Dashboard.
The username and password is _admin/admin_.

In the Fuel GUI ensure that the 2nd interface _(eth1)_ is configured as the public,
storage, management and private interface. Pictures of this can be found [here](/mirantis_pics.html)
### References

* [Notes on Building Mirantis Vagrant Box using packer]({% post_url 2016-02-07-building-mirantis-vagrant-box %})
* [Pictures from the Mirantis Virtual Setup](/mirantis_pics.html)
