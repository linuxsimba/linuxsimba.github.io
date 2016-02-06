---
title: "Openstack Heat - Creating a Project, Networks and Server only using Heat"
tags: ['openstack', 'heat']
---

First encountered [Openstack Heat](https://wiki.openstack.org/wiki/Heat) about 1
year ago when performing some
testing datacenter modeling using an Openstack environment.

The first goal was to figure out how to create enough VMs to understand how
Openstack networking works in a multi Tenant/Project environment.

### The topology

![basic switch/server topology](/openstack_topo1.png)

### Heat Resource File - create tenant users
First Openstack Heat resource file describes how to add a tenant user.
Use an Openstack admin user to do this.

{% gist 9636a23991278430cffb %}

### Heat Resource File - create networks and server
This Heat resource file is required to be run as the tenant user created in
the previous part.

{% gist 258abb1426d9dc1ef13b %}


### Heat Parameter File - create networks and server
This Heat parameters file defines an overlapping IP network. Floating IPs
are defined uniquely in the ``heat stack-create`` script.

{% gist 85d76ec71b3b2e5c9c9f %}

### Putting it all together

#### Run the heat resource and parameter files that create the tenant.
Because the new project/tenant user is going to be running Heat, the user must be a
member of the ``heat_admin`` role. Otherwise running ``heat stack-create`` as
the user ``demoadmin`` will fail.

```
$ cat keystonerc_admin

$ source keystronerc_admin
(keystonerc_admin)$ heat stack-create -f create_tenant_project_and_user.yml \
-P demo_project_name=demo_project1  \
-P demo_user_role=heat_admin \
-P demo_project_user=demoadmin \
-P demo_project_user_passwd=1luvopenstack \
project_demo1

```

#### Login as the newly tenant user
The [server resource definitions](http://docs.openstack.org/developer/heat/template_guide/openstack.html#OS::Nova::Server) do not define what tenant you want to add the servers to. So it seems like you are forced to login as the newly created tenant user before creating the servers

First check that there is ``keystonerc`` file for the new project/tenant use
created. If not, create one.
##### ``$ cat keystonerc_demo_user``
```
unset OS_SERVICE_TOKEN
export OS_USERNAME=demoadmin
export OS_PASSWORD=1luvopenstack
export PS1='[\u@\h \W(keystone_demo)]\$ '
export OS_AUTH_URL=http://192.168.100.1:5000/v2.0
export OS_TENANT_NAME=demo_project1
export OS_IDENTITY_API_VERSION=2.0
```

Then use the ``source`` bash keyword to logint as the newly created
project/tenant user.

```
$ source keystonerc_demo_user
```

#### Run the Heat script as the newly created tenant user

```
$(keystonerc_demo_user)$ heat stack-create -e tenant_network_server_params.yaml
\
-f openstack_heat_create_network_server.yaml \
project_demo1_as_demoadmin
```


### Problems yet to solve

Not sure how to view both heat stacks as a single user in Openstack.
First assumed that the ``admin`` user can view all the networks via the Horizon
Dashboard. I was suprised to see this is not so.
Hopefully in future releases, a ``Os::Nova::Server`` resource can be tied to a
tenant_id. If that is so, then only one heat stack is required.

