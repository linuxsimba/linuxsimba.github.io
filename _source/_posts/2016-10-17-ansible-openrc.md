---
title: Different Ways of Running Ad-hoc OpenStack commands Using Ansible
tags: ['vagrant', 'libvirt']
---


### Keystone variables in the commands

Walter Bentley, last year at AnsibleFest [demonstrated a way to execute openstack
commands](https://github.com/wbentley15/ansiblefest-demo).

```yaml

- name: Create user environments
  command: keystone --os-username={{ OS_USERNAME }} --os-password={{ OS_PASSWORD }} --os-tenant-name={{ OS_TENANT_NAME }} --os-auth-url={{ OS_AUTH_URL }} tenant-create --name={{ item }} --description="{{ item }}"
  with_items: tenantid
```

With this method you need to provide the OS\_USERNAME, OS\_AUTH_URL, OS\_PASSWORD into
the task. The recommendation is, of cause, to use [Ansible
Vault](http://docs.ansible.com/ansible/playbooks_vault.html) to encrypt this
information in the git repository.


### Use the raw Ansible keyword

Another way that I discovered was to use the
[raw](http://docs.ansible.com/ansible/raw_module.html) keyword that Ansible provides. It executes the ``openrc`` or ``keystonerc`` file on the host itself
then executes the OpenStack command.

```yaml

 name: |
   add the neutron-lbaas migration if lbaasv2 agent is installed.
   Seems to produce an error when it executes. Just ignore the error.
   Only run on a single controller in the clustered env.
  raw:  "source /root/openrc && neutron-db-manage --service lbaas upgrade head"
  args:
    executable: "/bin/bash"
  register: lbaas_install.changed == True
  delegate_to: "{{ groups['controller'][0] }}"
  ignore_errors: yes

```

### Write a module.

Ansible has some OpenStack configuration features [using
modules](http://docs.ansible.com/ansible/list_of_cloud_modules.html). A lot are
deprecated. I have not used any OpenStack modules yet. I have yet to write any module for managing
OpenStack. It would be interesting though to convert results from OpenStack Tempest into
Ansible facts.

