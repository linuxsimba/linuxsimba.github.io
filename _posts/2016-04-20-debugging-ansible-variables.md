---
title: "Debugging Ansible with_items errors"
tags: ['ansible']
---
I was recently porting some [openstack-ansible](https://github.com/openstack/oopenstack-ansible) code to another project and I experienced an interesting error.

```
TASK: [openstack_hosts | Adding new system tuning] ****************************
fatal: [localhost] => One or more undefined variables: 'unicode object' has no attribute 'key'
```

After much searching on the world's largest search engine, I found an interesting way to
identify the problem.

I used the [debug](http://docs.ansible.com/ansible/debug_module.html) ansible module and viewed the ``with_items`` part of the statement using the ``var`` debug module keyword.

After doing that I saw exactly what the problem was. A filter plugin was missing from my playbook :)

{%raw%}
```

TASK: [openstack_hosts | blah] ************************************************
fatal: [localhost] => Failed to template {{openstack_kernel_options}}: Failed to template {{ set_gc_val | int // 2 }}: Failed to template {{ gc_val if (gc_val | int <= 8192) else 8192 }}: Failed to template {{ ansible_memtotal_mb | default(1024) | bit_length_power_of_2 }}: template error while templating string: no filter named 'bit_length_power_of_2'

```
{% endraw %}

Here is the code that caused me so much grief for a little while.


### Task

{%raw%}
```
- name: Adding new system tuning
  sysctl:
    name: "{{ item.key }}"
    value: "{{ item.value }}"
    sysctl_set: "{{ item.set|default('yes') }}"
    state: "{{ item.state|default('present') }}"
    reload: "{{ item.reload|default('yes') }}"
  with_items: openstack_kernel_options
  ignore_errors: true
  tags:
    - openstack-host-kernel-tuning
```
{%endraw%}

### Variables

{%raw%}
```
#  the default set will be 1024 unless its defined by the user.
gc_val: "{{ ansible_memtotal_mb | default(1024) | bit_length_power_of_2 }}"
# The ste value has a Max allowable value of 8192 unless set by the user.
set_gc_val: "{{ gc_val if (gc_val | int <= 8192) else 8192 }}"

openstack_kernel_options:
  - { key: 'net.bridge.bridge-nf-call-arptables', value: 0 }
  - { key: 'net.ipv4.neigh.default.gc_thresh1', value: "{{ set_gc_val | int // 2 }}" }
```
{%endraw%}
