---
title: "Openstack Horizon Dashboard and VM Spice Console Via SSH Tunnels"
tags: ['openstack', 'console']
---

Recently had to deal with a Openstack Spice connectivity issue. Had to figure out how to connect to the virtual machine consoles when the controller node API network is behind a firewall.
The controller node API network is only accessible via a Jump host.

![spice connection](/spice_connection.svg)


## Gaining access to the Horizon Dashboard

In this example, the Horizon dashboard is hosted on the Controller node at _192.168.0.202/24_.

Set up a SSH Tunnel. Specify an unused TCP port on your local machine. Then provide the local port, remote IP address and remote port number of the Horizon dashboard portal.


```
ssh -L 9999:192.168.0.202:443 -p 16333 jumpserver.testbed.io
```
<i class="fa fa-info-circle"></i>
_[(Explain Shell)](http://explainshell.com/explain?cmd=ssh+-L+9999%3A192.168.0.202%3A443+-p+16333+jumpserver.testbed.io)_

After login, type in ``https://localhost:9999`` on your browser.

![horizon dashboard](/images/openstack_horizon.png)


## Gain access to the VM Console through a SSH tunnel.

The following configuration on the compute nodes provides access to the VM Console through the firewall.

### /etc/nova/nova.conf _(compute node)_

```
[spice]
agent_enabled = True
enabled = True
keymap = en-us
# Console Url and binds
html5proxy_base_url = http://localhost:6082/spice_auto.html
server_listen = 192.168.20.88
server_proxyclient_address = 192.168.20.88

[vnc]
enabled = False

# * 192.168.20.10 is the compute node host IP
```

Update the ssh port forwarding command provided when gaining access to the Horizon dashboard. The update creates a second SSH tunnel for VM console traffic.

```
ssh -L 9999:192.168.0.202:443 -L 6082:192.168.0.202:6082 -p 16333 jumpserver.testbed.io
```

On the Horizon dashboard the user will be presented a console connection link that looks something like this:

``https://localhost:6082/spice_auto.html?token=_(token string)_ ``

![spice console screen](/images/spice_console_screen.png)


## Solution Summary


* ``html5proxy_base_url`` determines the base url presented to the user on the horizon dashboard. In this case it starts with ``http://localhost:6082 ``

* The ``localhost:6082`` address maps to a SSH tunnel endpoint. On the other side of the SSH tunnel it connects to ``192.168.0.202:6082``.

* At the controller, there is a spice server proxy running on ``192.168.0.202:6082``.

* When the spice proxy server receives a connection request, it identifies the target based on the token in the URL, for example a Virtual Machine Spice console on the ``192.168.20.88`` compute node.

The reference docs are not super clear on this topic, especially if you not
a proxy or firewall expert. Through trial and error, it became clear how VM console proxy works.

## Reference
[ Official Openstack Remote Access Console Guide](http://docs.openstack.org/admin-guide-cloud/compute-remote-console-access.html)
