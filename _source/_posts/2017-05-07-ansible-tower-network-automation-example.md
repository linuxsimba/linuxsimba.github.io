---
title: "Simple Example of Network Automation using Ansible Tower"
tags: ['ansible', 'tower', 'network automation']
---

This is a simple example of how to setup Ansible Tower to automate a Cisco IOS Router.  This post is written from a network engineer's perspective.

> NOTE: Only tested with Ansible Tower 3.1.3 which uses Ansible 2.3 at the time this post was written

## Topology

The example setup was done in GNS3  using the Cisco ViRL IOS image and a RHEL 7.3 VM with a valid subscription(license).  Details of how this was done will be discussed in a future blog post.

![enter image description here](https://lh3.googleusercontent.com/-OsyWAaH3DFs/WQ9X3I40iwI/AAAAAAAAOOQ/rlGQYdqQNvMKQB9G8oxY41hr0YF4JjPUgCLcB/s0/tower_network_automation+%25281%2529.png "tower_network_automation &#40;1&#41;.png")

## Installing Ansible Tower

Follow the [Ansible Tower installation steps.](https://docs.ansible.com/ansible-tower/latest/html/quickinstall/) This demo uses the default account of ``admin``.

## Create a Test Playbook.

A test playbook called [test-network-automation can be found on Github](https://github.com/linuxsimba/test-network-automation). It contains one playbook called ``test.yml``,  that runs ``show version`` on the IOS router.

#### test.yml
```yaml
---
- hosts: switches
  connection: local
  vars:
    cli:
      host: "{{ inventory_hostname }}"
      username: "{{ vault_switch_username }}"
      password: "{{ vault_switch_password }}"

  tasks:
      - name: run show version
        ios_command:
          commands: "show version"
          provider: "{{ cli }}"
        register: show_version

      - name: print the show version output
        debug: var=show_version
```


## Configure the switch.

Here is the relevant IOS configuration

```
ip domain-name linuxsimba.local

!--- Generate an SSH key to be used with SSH.

crypto key generate rsa
ip ssh time-out 60
ip ssh authentication-retries 2
ip ssh version 2
username ansible privilege 15 password 0 1q2w3e4r5t!
```

```
rtr01#show ip ssh
SSH Enabled - version 1.99
Authentication methods:publickey,keyboard-interactive,password
Authentication Publickey Algorithms:x509v3-ssh-rsa,ssh-rsa
```
## Ansible Tower Configuration Workflow

The Ansible Tower setup to configure network automation can be summarized in the following flow chart

<div class="flow-chart"><svg height="510" version="1.1" width="836.5625" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="overflow: hidden; position: relative; top: -0.421875px;"><desc style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Created with Raphaël 2.1.2</desc><defs style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><path stroke-linecap="round" d="M5,0 0,2.5 5,5z" id="raphael-marker-block" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></path><marker id="raphael-marker-endblock33-obj242" markerHeight="3" markerWidth="3" orient="auto" refX="1.5" refY="1.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#raphael-marker-block" transform="rotate(180 1.5 1.5) scale(0.6,0.6)" stroke-width="1.6667" fill="black" stroke="none" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></use></marker><marker id="raphael-marker-endblock33-obj243" markerHeight="3" markerWidth="3" orient="auto" refX="1.5" refY="1.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#raphael-marker-block" transform="rotate(180 1.5 1.5) scale(0.6,0.6)" stroke-width="1.6667" fill="black" stroke="none" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></use></marker><marker id="raphael-marker-endblock33-obj244" markerHeight="3" markerWidth="3" orient="auto" refX="1.5" refY="1.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#raphael-marker-block" transform="rotate(180 1.5 1.5) scale(0.6,0.6)" stroke-width="1.6667" fill="black" stroke="none" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></use></marker><marker id="raphael-marker-endblock33-obj245" markerHeight="3" markerWidth="3" orient="auto" refX="1.5" refY="1.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#raphael-marker-block" transform="rotate(180 1.5 1.5) scale(0.6,0.6)" stroke-width="1.6667" fill="black" stroke="none" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></use></marker><marker id="raphael-marker-endblock33-obj246" markerHeight="3" markerWidth="3" orient="auto" refX="1.5" refY="1.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#raphael-marker-block" transform="rotate(180 1.5 1.5) scale(0.6,0.6)" stroke-width="1.6667" fill="black" stroke="none" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></use></marker><marker id="raphael-marker-endblock33-obj247" markerHeight="3" markerWidth="3" orient="auto" refX="1.5" refY="1.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#raphael-marker-block" transform="rotate(180 1.5 1.5) scale(0.6,0.6)" stroke-width="1.6667" fill="black" stroke="none" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></use></marker><marker id="raphael-marker-endblock33-obj248" markerHeight="3" markerWidth="3" orient="auto" refX="1.5" refY="1.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#raphael-marker-block" transform="rotate(180 1.5 1.5) scale(0.6,0.6)" stroke-width="1.6667" fill="black" stroke="none" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></use></marker></defs><rect x="0" y="0" width="52.6875" height="39" rx="20" ry="20" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="st" transform="matrix(1,0,0,1,112.8125,4)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="stt" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,112.8125,4)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Start</tspan></text><rect x="0" y="0" width="121.4375" height="39" rx="0" ry="0" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="op1" transform="matrix(1,0,0,1,78.4375,97)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="op1t" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,78.4375,97)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Create a Project</tspan></text><rect x="0" y="0" width="270.3125" height="39" rx="0" ry="0" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="op2" transform="matrix(1,0,0,1,4,190)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="op2t" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,4,190)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Configure an Empty Machine Credential</tspan></text><rect x="0" y="0" width="145.109375" height="39" rx="0" ry="0" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="op3" transform="matrix(1,0,0,1,390.9141,190)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="op3t" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,390.9141,190)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Create an Inventory</tspan></text><rect x="0" y="0" width="147.515625" height="39" rx="0" ry="0" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="op4" transform="matrix(1,0,0,1,389.7109,283)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="op4t" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,389.7109,283)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Create a Host Group</tspan></text><rect x="0" y="0" width="201.890625" height="39" rx="0" ry="0" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="op5" transform="matrix(1,0,0,1,362.5234,376)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="op5t" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,362.5234,376)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Add a host to the Host Group</tspan></text><rect x="0" y="0" width="161.984375" height="39" rx="0" ry="0" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="op6" transform="matrix(1,0,0,1,672.5781,376)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="op6t" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,672.5781,376)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Create a Job Template</tspan></text><rect x="0" y="0" width="158.15625" height="39" rx="0" ry="0" fill="#ffffff" stroke="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);" stroke-width="2" class="flowchart" id="op7" transform="matrix(1,0,0,1,674.4922,469)"></rect><text x="10" y="19.5" text-anchor="start" font-family="sans-serif" font-size="14px" stroke="none" fill="#000000" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); text-anchor: start; font-family: sans-serif; font-size: 14px; font-weight: normal;" id="op7t" class="flowchartt" font-weight="normal" transform="matrix(1,0,0,1,674.4922,469)"><tspan dy="4.5" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);">Run the Job Template</tspan><tspan dy="18" x="10" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0);"></tspan></text><path fill="none" stroke="#000000" d="M139.15625,43C139.15625,43,139.15625,82.65409994125366,139.15625,94.00043908460066" stroke-width="2" marker-end="url(#raphael-marker-endblock33-obj242)" font-family="sans-serif" font-weight="normal" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); font-family: sans-serif; font-weight: normal;"></path><path fill="none" stroke="#000000" d="M139.15625,136C139.15625,136,139.15625,175.65409994125366,139.15625,187.00043908460066" stroke-width="2" marker-end="url(#raphael-marker-endblock33-obj243)" font-family="sans-serif" font-weight="normal" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); font-family: sans-serif; font-weight: normal;"></path><path fill="none" stroke="#000000" d="M274.3125,209.5C274.3125,209.5,369.66375866532326,209.5,387.9145855192328,209.5" stroke-width="2" marker-end="url(#raphael-marker-endblock33-obj244)" font-family="sans-serif" font-weight="normal" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); font-family: sans-serif; font-weight: normal;"></path><path fill="none" stroke="#000000" d="M463.46875,229C463.46875,229,463.46875,268.65409994125366,463.46875,280.00043908460066" stroke-width="2" marker-end="url(#raphael-marker-endblock33-obj245)" font-family="sans-serif" font-weight="normal" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); font-family: sans-serif; font-weight: normal;"></path><path fill="none" stroke="#000000" d="M463.46875,322C463.46875,322,463.46875,361.65409994125366,463.46875,373.00043908460066" stroke-width="2" marker-end="url(#raphael-marker-endblock33-obj246)" font-family="sans-serif" font-weight="normal" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); font-family: sans-serif; font-weight: normal;"></path><path fill="none" stroke="#000000" d="M564.4140625,395.5C564.4140625,395.5,652.1030224859715,395.5,669.5723074831767,395.5" stroke-width="2" marker-end="url(#raphael-marker-endblock33-obj247)" font-family="sans-serif" font-weight="normal" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); font-family: sans-serif; font-weight: normal;"></path><path fill="none" stroke="#000000" d="M753.5703125,415C753.5703125,415,753.5703125,454.65409994125366,753.5703125,466.00043908460066" stroke-width="2" marker-end="url(#raphael-marker-endblock33-obj248)" font-family="sans-serif" font-weight="normal" style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); font-family: sans-serif; font-weight: normal;"></path></svg></div>


### Configure a Project
Add the test playbook into the Tower database. This is done by creating [a Project](http://docs.ansible.com/ansible-tower/latest/html/userguide/projects.html)

![enter image description here](https://lh3.googleusercontent.com/-USrG6izfs64/WQ_SVLA2l2I/AAAAAAAAOOw/LJhbyk9CfhIq1j-E0w5zkKOdQWf5amR2gCLcB/s0/tower_create_project.png "tower_create_project.png")


### Configure an Empty Machine Credential

Because the connection made to the IOS device is made via a proxy connection on the Ansible tower server, all one has to do is create an _empty_ machine credential. That is, just give the credential a name. For this example, because [Ansible Vault](http://docs.ansible.com/ansible/playbooks_vault.html) is used , the ``Vault password`` is filled out.  The Vault Password is ``tower``. It is good practise to encrypt your network authentication. Tower does provide a feature called [Network Credentials](http://docs.ansible.com/ansible-tower/latest/html/userguide/credentials.html) but it will not be covered on this post. The method of encrypting network authentication information within the playbook was preferred.

![enter image description here](https://lh3.googleusercontent.com/-V3J9rZFYd3k/WQ_SvbfI_8I/AAAAAAAAOO4/GY8iCLRwS0E4jzRbCfv-ZHursmBeFVvogCLcB/s0/tower_creds_machine.png "tower_creds_machine.png")


### Create an Inventory

An inventory is a database of hosts and grouping of hosts that are referenced in the playbook. In the test playbook, the host group called ``switches`` is referenced. Tower will host this database so that the playbook just references it.

![enter image description here](https://lh3.googleusercontent.com/-TBW0dZm7g44/WQ_TLKhgQjI/AAAAAAAAOPA/sB55qEqQZAMUMrrWk7L526C2T27M_plCACLcB/s0/tower1_create_inventory.png "tower1_create_inventory.png")

#### Create a Host Group
This step creates the ``switches`` host group.  Hosts added with this group will execute the ``show version`` action in the tasks list of the text playbook.

![enter image description here](https://lh3.googleusercontent.com/-KA3WLAuyIqU/WQ_TslAlmMI/AAAAAAAAOPQ/addpf82ojsEkCo3MPC32FfYBlF7neNFFgCLcB/s0/tower_create_group.png "tower_create_group.png")

#### Add Hosts to the Host Group
Only 1 network device is listed in this demo. It is called ``switch01`` and its IP is ``192.168.0.100``. Note that the IP is defined in the variable ``ansible_host``.

![enter image description here](https://lh3.googleusercontent.com/-MuHZu_uLIqM/WQ_UA5DGXfI/AAAAAAAAOPc/19UOa__j5MYq1CDgIsXgzm0kNk1JDoxNgCLcB/s0/tower_create_host.png "tower_create_host.png")

### Create a Job Template
Create a object called a Job template. This brings together all the information entered before. For a network automation job, one creates a job template with an empty machine credential, a reference to  a playbook. This playbook uses the local connection type, `` connection: local``. Network authentication is set within the playbook and not in Tower using what Ansible Core (CLI) calls a ``network provider``. In this case the provider is a variable hash called ``cli``.

![enter image description here](https://lh3.googleusercontent.com/-4vighlSuDe4/WQ_U7QO-IDI/AAAAAAAAOPw/vyf5fcag6m0Vv5OjqpeZWrd-loj8eSa1QCLcB/s0/tower_create_job.png "tower_create_job.png")

### Run the Job Template
Finally run the job template. This creates what Tower calls a  _Job_. Below are the results of executing the job.

![enter image description here](https://lh3.googleusercontent.com/-qAnzOCT02HA/WQ_Va9Q7D-I/AAAAAAAAOQQ/77fDz8kNBQAz5sXJ4k93vJLcjtBb2cV2wCLcB/s0/tower_start_job.png "tower_start_job.png")

![enter image description here](https://lh3.googleusercontent.com/-AqFpRDzWwLM/WQ_VG8n0CdI/AAAAAAAAOQI/-o8TubpBOdwARKRV3o4Zda8fbOgUtvUHwCLcB/s0/tower_result_of_job.png "tower_result_of_job.png")



### Reference

* [Test Network Automation Playbook](https://github.com/linuxsimba/test-network-automation)
* [Ansible Tower Installation Guide](https://docs.ansible.com/ansible-tower/latest/html/quickinstall/)
* [Ansible Tower Admin Reference Guide](https://docs.ansible.com/ansible-tower/latest/html/administration/)
* [Network Device Authentication using Ansible 2.3](https://www.ansible.com/blog/network-device-authentication-with-ansible-2-3)

> Written with [StackEdit](https://stackedit.io/).
