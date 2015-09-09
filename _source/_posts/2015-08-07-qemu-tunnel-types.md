---
title: A Study on QEMU Netdev Tunnel Types
tags: ['vagrant', 'libvirt', 'ruby', 'qemu']
---


About 2 years ago, I [began exploring stitching virtual machine(VM)](https://github.com/skamithi/ptmd_demo) interfaces together directly using QEMU.  The reason for doing this is because connecting VMs together using linux bridges has the following disadvantages:

1. VMs cannot see each other LLDP frames. These are consumed by the host OS
2. BPDUs between VMs are also consumed by the Host OS

So you cannot tie two bridges within the VMs together to form a larger broadcast domain.

![expanding bridge domain](https://lh3.googleusercontent.com/8ppdp-gtSD9NGfvvTLFUhKUwuhgo0YVdKbZX2lkTudQ=s0 "bridges.png")

So the way I did this was to use [QEMU netdev sockets](http://wiki.qemu.org/Documentation/Networking). It supports 3 modes

* TCP Tunnel
* Multicast Tunnel
* UDP Unicast Tunnel


### TCP Tunnels
In this mode, one side of the connection starts a TCP server, while the other side binds to it. Using libvirt the config looks like this

```
...
  <devices>
    <interface type='server'>
      <source address='127.0.0.1' port='5558'/>
    </interface>
    ...
    <interface type='client'>
      <source address='127.0.0.1' port='5558'/>
    </interface>
  </devices>
  ...
```

_([Reference](https://libvirt.org/formatdomain.html#elementsNICSTCP))_

It works great, with one **major problem**. Reboot the VM with the "server" connection and the tcp connection does not come up again. I have to reboot the client side as well.

With a small topology this is fine, but 20 VMs each with 6 or 7 NICs connected to each. Say in a [Leaf Spine or CLOS topology](https://blog.westmonroepartners.com/a-beginners-guide-to-understanding-the-leaf-spine-network-topology/). I would see myself doing a kinda a dance rebooting VMs in a particular sequence to ensure all the links come up properly.

###  Multicast Tunnel
In this mode, UDP multicast is used to stitch the VM NICs together. I noticed I
had to use the *same* multicast address for all interfaces, just switch the port numbers to get the links to come up. Here is a small example

```
  <devices>
    <interface type='mcast'>
      <source address='239.255.1.1' port='5558'/>
    </interface>
    ...
    <interface type='mcast'>
      <source address='239.255.1.1' port='5558'/>
    </interface>
  </devices>
  ...
```
_([Reference](https://libvirt.org/formatdomain.html#elementsNICSMulticast))_

Everything comes up except for one thing. LLDP and BPDU packets are looped back
to the source interface. Quite annoying! [A bug was filed on this in 2010](https://bugzilla.redhat.com/show_bug.cgi?id=557188), but was closed as WONTFIX.


### UDP Unicast Tunnels

In this mode, a udp unicast tunnel is created. It has a source IP & Port and
Destination IP & Port configuration.  An example is shown below:

```
<devices>
    <interface type='udp'>
      <source address='127.0.0.1' port='5558'/>
      <dest address='127.0.0.1' port='6667' />
    </interface>
    ...
    <interface type='udp'>
      <source address='127.0.0.1' port='6667'/>
      <dest address='127.0.0.1' port='5558' />
    </interface>
  </devices>
```

>**Note**: This configuration is not supported in the latest libvirt. [A patch
>has been
>submitted](https://www.redhat.com/archives/libvir-list/2015-August/msg00262.html)
>to add this support. If you run Ubuntu 14.04 you can use [my patched libvirt on
>my PPA](https://launchpad.net/~linuxsimba/+archive/ubuntu/libvirt-udp-tunnel)

I have done reboot tests and this appears to be the **most stable** way to stitch point to point connections between VMs. It is way GNS3 does it at least :)


## Vagrant-Libvirt

I have a [branch in my fork of
vagrant-libvirt](https://github.com/skamithi/vagrant-libvirt/tree/mcast_and_tcp_tunnel_support)
where I add support for all the above tunneling modes.  I will send a pull
request to the [master vagrant-libvirt
project](https://github.com/pradels/vagrant-libvirt) once I find out if libvirt will accept the udp unicast tunneling patch. An example VagrantFile is shown below

### Topology
![vagrant topology](https://lh3.googleusercontent.com/F9ERg4jd0nXK5nmlhTaVHTvV330FtvSloBtKq8VC3bQ=s0
"topology.png")

### VagrantFile
```ruby
Vagrant.configure(2) do |config|
  config.vm.box = 'jessie'
  # vagrant issues #1673..fixes hang with configure_networks
  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"

  config.vm.define :test1 do |node|
    node.vm.provider :libvirt do |domain|
      domain.memory = 256
    end
    # disabling sync folder support on all VMs
    node.vm.synced_folder '.', '/vagrant', :disabled => true

    # test1vm(eth1) === test2vm(eth1)
    node.vm.network :private_network,
      :libvirt__tunnel_type => 'udp',
      :libvirt__tunnel_port => '8000',
      :libvirt__tunnel_local_port => '9000'

    # test1vm(eth2) ==== test2vm(eth2)
    node.vm.network :private_network,
      :libvirt__tunnel_type => 'udp',
      :libvirt__tunnel_port => '8001',
      :libvirt__tunnel_local_port => '9001'
  end
   config.vm.define :test2 do |node|
    node.vm.provider :libvirt do |domain|
      domain.memory = 256
    end
    # disabling sync folder support on all VMs
    node.vm.synced_folder '.', '/vagrant', :disabled => true

    # test2vm(eth1) === test1vm(eth1)
    node.vm.network :private_network,
      :libvirt__tunnel_type => 'udp',
      :libvirt__tunnel_port => '9000',
      :libvirt__tunnel_local_port => '8000'

    # test2vm(eth2) ==== test1vm(eth2)
    node.vm.network :private_network,
      :libvirt__tunnel_type => 'udp',
      :libvirt__tunnel_port => '9001',
      :libvirt__tunnel_local_port => '8001'
  end
end

```

I plan on updating [my PTMD demo](https://github.com/skamithi/ptmd_demo) using Vagrant sometime this year..Will blog about that too when its done.

> Written with [StackEdit](https://stackedit.io/).


